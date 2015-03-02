import datetime

from jasmine.result_list import ResultList


class ConsoleFormatter(object):
    COLORS = {
        'red': "\033[0;31m",
        'green': "\033[0;32m",
        'yellow': "\033[0;33m",
        'none': "\033[0m"
    }

    JASMINE_HEADER = """
      _                     _
     | |                   (_)
     | | __ _ ___ _ __ ___  _ _ __   ___
 _   | |/ _` / __| '_ ` _ \| | '_ \ / _ \\
| |__| | (_| \__ \ | | | | | | | | |  __/
 \____/ \__,_|___/_| |_| |_|_|_| |_|\___|

"""

    def __init__(self, results, **kwargs):
        self.colors = kwargs.get('colors', True)
        self.browser_logs = kwargs.get('browser_logs', [])
        self.suite_results = ResultList(kwargs.get('suite_results', []))
        self.results = ResultList(results)


    def format(self):
        return (
            self.JASMINE_HEADER +
            self.format_progress() + "\n\n" +
            self.format_summary() + "\n\n" +
            self.format_suite_failure() + "\n\n" +
            self.format_browser_logs() +
            self.format_failures() +
            self.format_pending()
        )

    def format_progress(self):
        output = ""

        for result in self.results:
            if result.status == "passed":
                output += self._colorize('green', '.')
            elif result.status == "failed":
                output += self._colorize('red', 'X')
            else:
                output += self._colorize('yellow', '*')

        return output

    def format_summary(self):
        output = "{0} specs, {1} failed".format(
            len(self.results),
            len(list(self.results.failed()))
        )

        if self.results.pending():
            output += ", {0} pending".format(len(list(self.results.pending())))

        return output

    def format_suite_failure(self, colors=False):
        output = ""
        for result in self.suite_results:
            if result.failedExpectations:
                output += self._colorize(
                    'red',
                    '\nAfter All {0}'.format(
                        result.failedExpectations[0]['message']
                    )
                )
        return output

    def format_browser_logs(self):
        output = ""
        if list(self.results.failed()) and self.browser_logs:
            output = "Browser Session Logs:\n"
            for log in self.browser_logs:
                output += "  [{0} - {1}] {2}\n".format(
                    datetime.datetime.fromtimestamp(log['timestamp'] / 1000.0),
                    log['level'],
                    log['message']
                )
            output += "\n"
        return output

    def format_failures(self):
        output = ""
        for failure in self.results.failed():
            output += (
                self._colorize('red', failure.fullName)
                + "\n  "
                + failure.failedExpectations[0]['message']
                + "\n  "
                + self.clean_stack(failure.failedExpectations[0]['stack'])
                + "\n"
            )

        return output

    def clean_stack(self, stack):
        if not stack:
            return ""

        def dirty(stack_line):
            return "__jasmine__" in stack_line or "__boot__" in stack_line

        return "\n".join([
            stack_line
            for stack_line in stack.split("\n")
            if not dirty(stack_line)
        ])

    def format_pending(self):
        output = ""

        for pending in self.results.pending():
            output += self._colorize('yellow', pending.fullName + "\n")
            if pending.pendingReason:
                output += "  Reason: {0}\n".format(pending.pendingReason)

        return output

    def _colorize(self, color, text):
        if not self.colors:
            return text

        return self.COLORS[color] + text + self.COLORS['none']

