/* ***********************************

The Chaos Bonobo Server

Author: CostisC

 *********************************** */


'use strict';

const yargs = require('yargs');
const yaml = require('js-yaml');
const fs = require('fs')
const log4js = require('log4js')
const {join} = require('path')
const crypto = require('crypto')
const express = require('express');
const bodyParser = require('body-parser');
const { fail } = require('assert');

/**
 * Translate timestamp signatures into epoch time.
 * Possible input formats:
 * '2023 10 3'
 * '2023-10-3T13:00'
 * '23:54'
 * '1h 35m'   (1h and 35min after current time)
 * etc.
 * @param {string} date_input - timestamp signature
 * @param {number} time_reference - duration w.r.t this time reference (in epoch time);
 *  if not set, the reference is now
 * @returns {number} Epoch time
 */
function parse_timestamp(date_input, time_reference=NaN)
{
    let timestamp = (isNaN(time_reference))? new Date() : new Date(time_reference);
    let epoch_time;
    // First, check if a '_h _m' notation
    let matchArray = [...date_input.matchAll(/(\d+)([mh])/g)];
    if (matchArray.length) {
        epoch_time = timestamp.getTime();
        for (let arr of matchArray) {
            let dt = (arr[2] === 'h') ? arr[1] * 3600e+3 :
                     (arr[2] === 'm') ? arr[1] * 60e+3 : 0;
            epoch_time += dt;
        }
        return epoch_time;
    }
    let date_time_format = date_input;
    // if time-only, default to today
    if (date_input.search(/^\d+:\d+/) != -1) {
        date_time_format = `${timestamp.toDateString()} ${date_input}`;
    }
    epoch_time = Date.parse(date_time_format);
    if (isNaN(epoch_time))
        throw Error(`Invalid date format: ${date_input}`);
    return epoch_time;

}

const md5sum = (obj) => crypto.createHash('md5').update(JSON.stringify(obj)).digest('hex');

const zeroPad = (num) => String(num).padStart(2,'0');

const date_smart_format = (epoch, current_time) => {
    let tmstp = new Date(epoch);
    let smart_date = `${zeroPad(tmstp.getHours())}:${zeroPad(tmstp.getMinutes())}`;
    if (current_time.getDate() != tmstp.getDate()) {
        smart_date += ` (${zeroPad(tmstp.getDate())}/${zeroPad(tmstp.getMonth()+1)})`;
    }
    return smart_date;
}

/**
 * Parse and prepare the experiments input
 * @param {object} experiment_dict - dictionary of the exeperiment input
 * @returns {object} dictionary of parsed experiment
 */
function parse_experiments(experiment_dict)
{
    let manifest = {};
    let now = new Date();
    for (var element of experiment_dict) {
        var bFilled = false;
        for (let failure of element.failures) {
            if ((failure.disable || false) === false) {
                if (!manifest[element.host])
                    manifest[element.host] = {failures: []};
                try {
                    failure.start = parse_timestamp(failure.start || '0m');
                    failure.duration = parse_timestamp(failure.duration || '0m', failure.start);
                    if (failure.duration < failure.start)
                        throw new Error("Stop time is older that start time")
                } catch (err) {
                    logger.error(`Failed to parse timestamp in \
${element.host} : ${failure.type} (${err.message})`);
                    continue
                }
                // remove any passed experiments
                if (failure.start < now.getTime())
                    continue;
                manifest[element.host].failures.push(failure);
                bFilled = true

                let start = date_smart_format(failure.start, now);
                let stop = date_smart_format(failure.duration, now);
                logger.log(`Experiment Loaded => host: ${element.host}, \
experiment: ${failure.type}, duration: ${start} - ${stop}`);
            }
        }
        // a checksum for each host, so to be able to check any future changes
        if (bFilled)
            manifest[element.host]['hash'] = md5sum(manifest[element.host]['failures'])
    }
    return manifest;
}

const read_experiments = (experiment_file) => {
    try {
        var experiment_dict = yaml.load(fs.readFileSync(experiment_file, 'utf8'));
    } catch (e) {
        if (e instanceof yaml.YAMLException)
            logger.error(`Error in parsing '${experiment_file}'\n${e.message}`);
        else
            logger.error(`Cannot read '${experiment_file}' settings file ${e.message}`);
        process.exit(1);
    }
    return parse_experiments(experiment_dict);
    //console.log(JSON.stringify(experiments, null, " "));
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */
/* ================ MAIN ================= */
/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

let experiments;
process.on('SIGUSR1', () => {
    logger.log("Requested experiment manifast update");
    experiments = read_experiments(experiment_file);

});

log4js.configure(__dirname + '/logger.json');
var logger = log4js.getLogger();

const argv = yargs
    .option('port', {
        description: 'The listening port',
        default: 4440,
        alias: 'p',
        type: 'string'
    })
    .option('experiment', {
        description: 'The experiment description',
        default: 'experiment.yaml',
        alias: 'e',
        type: 'string'
    })
    .help()
    .alias('help', 'h').argv;

// Load configuration
const experiment_file = (argv.experiment[0] === '/')? argv.experiment :
     __dirname + '/' + argv.experiment;


experiments = read_experiments(experiment_file);


const app = express();
app.disable('x-powered-by');
app.disable('etag');

app.use('/docs', express.static(join(__dirname, 'docs')))

const notFound = (req, res) => {
    logger.debug(`Request not found: ${req.path}`)
    res.status(404).end();
}

app.get('/experiments/:host', (req, res, next) => {
    let experiment = experiments[req.params.host];
    let hash = req.query.hash;
    if (!experiment)
            return next();
    if (hash && hash === experiment.hash)
            return res.end();

    return res.send(experiment);
});


app.post('/notify', bodyParser.text(), (req, res) => {
    let level = req.query.level || 'info';
    switch(level) {
        case "error":
            logger.error(req.body);
            break;
        case "warn":
            logger.warn(req.body);
            break;
        case "info":
        default:
            logger.info(req.body);
    }
    res.end();

});

app.use(notFound);

// ********** Start of Service *********** //
app.listen(argv.port, () => {
        logger.info(`Server started on port :${argv.port}`);
}).on('error', (e) => {
        logger.error(`Server failed to start: '${e}'`)
  })
