"""Analog analysis module."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import datetime
import re
import time

from analog.exceptions import MissingFormatError
from analog.formats import LogFormat
from analog.report import Report


class Analyzer:

    """Log analysis utility.

    Scan a logfile for logged requests and analyze calculate statistical metrics
    in a :py:class:`analog.report.Report`.

    """

    MAX_AGE = 10

    def __init__(self, log, format, paths=[], max_age=MAX_AGE):
        """Configure log analyzer.

        :param log: handle on logfile to read and analyze.
        :type log: :py:class:`io.TextIOWrapper`
        :param format: log format identifier or regex pattern.
        :type format: ``str``
        :param paths: Paths to explicitly analyze. If not defined, paths are
            detected automatically.
        :type paths: ``list`` of ``str``
        :param max_age: Max. age of log entries to analyze in minutes.
        :type max_age: ``int``
        :raises: :py:class:`analog.exceptions.MissingFormatError` if no
            ``format`` is specified.

        """
        self._log = log
        if not format:
            raise MissingFormatError(
                "Require log format. Specify format name or regex pattern.")
        formats = LogFormat.all_formats()
        if format in formats:
            self._format = formats[format]
        else:
            self._format = LogFormat('custom', re.escape(format))
        self._pathconf = paths

        self._max_age = max_age

        # execution time
        self.execution_time = None

    def _monitor_path(self, path):
        """Convert full request path to monitored path.

        If no path groups are configured to be monitored, all full paths are.

        :param path: the full request path.
        :type path: ``str``
        :returns: the monitored path (part of ``path``) or ``None`` if not
            monitored.
        :rtype: ``str`` or ``None``

        """
        if not self._pathconf:
            return path
        for monitored in self._pathconf:
            if path.startswith(monitored):
                return monitored
        return None

    def _timestamp(self, time_str):
        """Convert timestamp strings from nginx to datetime objects.

        Format is "15/Jan/2014:14:12:50 +0000".

        :returns: request timestamp datetime.
        :rtype: :py:class:`datetime.datetime`

        """
        return datetime.datetime.strptime(time_str, self._format.time_format)

    def __call__(self):
        """Analyze defined logfile.

        :returns: log analysis report object.
        :rtype: :py:class:`analog.report.Report`

        """
        self._now = datetime.datetime.now()
        self._now = self._now.replace(second=0, microsecond=0)
        self._min_time = self._now - datetime.timedelta(minutes=self._max_age)

        # start timestamp
        started = time.clock()

        report = Report()

        # read lines from logfile for the last max_age minutes
        for line in self._log:
            # parse line
            match = self._format.pattern.search(line)
            if match is None:
                continue
            log_entry = self._format.entry(match)

            # don't process anything older than MAX_AGE
            timestamp = self._timestamp(log_entry.timestamp)
            if timestamp < self._min_time:
                continue
            # stop processing when now was reached
            if timestamp > self._now:
                break

            # parse request
            path = self._monitor_path(log_entry.path)
            if path is None:
                continue

            # collect the numbers
            report.add(
                path=path,
                verb=log_entry.verb,
                status=int(log_entry.status),
                time=float(log_entry.request_time),
                upstream_time=float(log_entry.upstream_response_time),
                body_bytes=int(log_entry.body_bytes_sent))

        # end timestamp
        finished = time.clock()
        report.execution_time = finished - started

        return report


def analyze(log, format, paths=[], max_age=Analyzer.MAX_AGE,
            path_stats=False):
    """Convenience wrapper around :py:class:`analog.analyzer.Analyzer`.

    :param log: handle on logfile to read and analyze.
    :type log: :py:class:`io.TextIOWrapper`
    :param format: log format identifier or regex pattern.
    :type format: ``str``
    :param paths: Paths to explicitly analyze. If not defined, paths are
        detected automatically.
    :type paths: ``list`` of ``str``
    :param max_age: Max. age of log entries to analyze in minutes.
    :type max_age: ``int``
    :param path_stats: Print per-path analysis report. Default off.
    :type path_stats: ``bool``
    :returns: log analysis report object.
    :rtype: :py:class:`analog.report.Report`

    """
    analyzer = Analyzer(log=log, format=format, paths=paths, max_age=max_age)
    return analyzer()
