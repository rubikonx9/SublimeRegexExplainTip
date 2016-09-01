"""
RegexExplainTip plugin for Sublime Text 3.
"""

import re
import subprocess

import sublime
import sublime_plugin


class RegexexplaintipCommand(sublime_plugin.TextCommand):
    """
    The only class for this plugin.
    """
    REGEX_SUBSTITUTIONS = [
        (r"&",                         "&amp;"),
        (r"<",                         "&lt;"),
        (r">",                         "&gt;"),
        (r"\s",                        "&nbsp;"),
        (r"(\\[^&]|\\&nbsp;)",         """<span class=\"literal\">
                                              \\g<1>
                                          </span>
                                       """),
        (r"([\^\.\$\|])",              """<span class=\"meta\">
                                              \\g<1>
                                          </span>
                                       """),
        (r"([\[\]\(\)])",              """<span class=\"bracket\">
                                              \\g<1>
                                          </span>
                                       """),
        (r"([\+\*\?]|\{\d+(,\d+)?\})", """<span class=\"quantifier\">
                                              \\g<1>
                                          </span>
                                       """)
    ]

    EXPLANATION_SUBSTITUTIONS = [
        # Magic: http://stackoverflow.com/questions/23205606/regex-to-remove-comma-between-double-quotes-notepad
        (r" (?=[^']*'[^']*(?:'[^']*'[^']*)*$)", " <space> "),
        (r"&",                                  "&amp;"),
        (r"<",                                  "&lt;"),
        (r">",                                  "&gt;"),
        (r"\"",                                 "&quot;"),
        (r"'(.*?)'",                            """<span class=\"literal\">
                                                       \\g<1>
                                                   </span>
                                                """),
        (r"(\\.)",                              """<span class=\"literal\">
                                                       \\g<1>
                                                   </span>
                                                """),
        (r"(OR|\^|\$|\.|\\\d+)",                """<span class=\"meta\">
                                                       \\g<1>
                                                   </span>
                                                """),
        (r"((between \d+ and )?\d+" +
         r" (or more )?times|optional)",        """<span class=\"quantifier\">
                                                       \\g<1>
                                                   </span>
                                                """)
    ]

    def __init__(self, view):
        """
        Reads CSS content from file.
        """
        super(RegexexplaintipCommand, self).__init__(view)

        self.was_actual_rule = False

        self.load_css()

    def load_css(self):
        """
        Loads CSS from file and stores it as object property.
        """
        css_file = "Packages/RegexExplainTip/css/default.css"

        self.css = sublime.load_resource(css_file).replace("\r", "")

    def get_selected_text(self):
        """
        Obtains the text under cursor (current selection).
        """
        region        = self.view.sel()[0]
        selected_text = self.view.substr(region)

        return selected_text

    def get_explanation(self, regex):
        """
        Calls Perl to get the textual explan\\ation of the regex.
        """
        command = """
            use YAPE::Regex::Explain;

            my $explanation = YAPE::Regex::Explain->new("%s")->explain('regex');

            print $explanation;
        """ % re.sub("\\\\", "\\\\\\\\", regex)

        out, _ = subprocess.Popen([ "perl", "-e", command ], stdout = subprocess.PIPE).communicate()

        return out.decode("utf-8")

    def partition_by_empty_line(self, lines):
        """
        Splits an array into array of arrays, treating an empty string (\n only) as a delimiter.
        """
        partitioned       = []
        current_partition = []

        for line in lines:
            if re.match("^$", line):
                partitioned.append(current_partition)
                current_partition = []
            else:
                current_partition.append(line)

        return partitioned

    def extract_regex_and_explanation(self, rules):
        """
        Creates a list of objects (regex - explanation pairs) from lists of lines.
        """
        result = []

        for rule in rules:
            regex_parts       = []
            explanation_parts = []

            for line in rule:
                regex, explanation = self.split_by_middle_hash(line)

                regex_parts.append(regex)
                explanation_parts.append(explanation)

            result.append({
                "regex"       : "".join(regex_parts).strip(),
                "explanation" : "".join(explanation_parts).strip()
            })

        return result

    def convert_lines_to_html(self, lines):
        """
        Converts the lines to a full explanation message.
        """
        lines = lines[5:-3]  # Remove heading & tail (not very useful info on regex flags)

        rules = self.extract_regex_and_explanation(
            self.partition_by_empty_line(lines)
        )

        return "".join(
            map(self.convert_rule_to_html, rules)
        )

    def convert_rule_to_html(self, rule):
        """
        Converts a single rule to an HTML structure.
        """
        regex       = rule["regex"]
        explanation = rule["explanation"]

        if regex.endswith("\\"):
            # Restore required trailing space
            regex = regex + " "

        separator = """
            <div class=\"separator-outer\">
                <div class=\"separator-inner\">
                </div>
            </div>
        """ if self.was_actual_rule else ""

        # Check for start of capture group
        group_start_match = re.match(r"(group and capture to \\(\d+)|" +
                                     r"group, but do not capture|" +
                                     r"look ahead to see if there is(?: not)?)(.*)", explanation)

        if group_start_match:
            self.was_actual_rule = False

            group_type           = group_start_match.group(1)
            capture_group_number = group_start_match.group(2) if group_start_match.group(2) else ""
            additional_info      = re.sub(r":$", "", group_start_match.group(3).strip())

            if group_type.startswith("group and capture"):
                group_type = "Capture group"
            elif group_type.startswith("group, but"):
                group_type = "Non-capture group"
            elif group_type.find("not") != -1:
                group_type = "Negative look-ahead"
            else:
                group_type = "Look-ahead"

            return """
                <div class=\"group-outer level-%s\">
                    <div class=\"group-inner\">
                        <div class=\"group-info-header\">
                            %s
                            <span class=\"meta\">
                                %s
                            </span>
                            %s
                        </div>
            """ % (
                capture_group_number,
                group_type,
                capture_group_number,
                self.replace_by_patterns(additional_info, self.EXPLANATION_SUBSTITUTIONS)
            )

        # Check for end of capture group
        group_end_match = re.match(r"end of (?:\\\d+|grouping|look-ahead)\s?(.*)", explanation)

        if group_end_match:
            self.was_actual_rule = False

            additional_info = group_end_match.group(1)

            footer = """
                <div class=\"group-info-footer\">
                    %s
                </div>
            """ % self.replace_by_patterns(additional_info, self.EXPLANATION_SUBSTITUTIONS)

            return """
                        %s
                        %s
                    </div>
                </div>
            """ % (
                separator if additional_info else "",
                footer if additional_info else ""
            )

        self.was_actual_rule = True

        # Regular case
        return """
            %s
            <div class=\"rule\">
                <div class=\"regex\">
                    <code>
                        %s
                    </code>
                </div>
                <div class=\"explanation\">
                    %s
                </div>
            </div>
        """ % (
            separator,
            self.replace_by_patterns(regex,       self.REGEX_SUBSTITUTIONS),
            self.replace_by_patterns(explanation, self.EXPLANATION_SUBSTITUTIONS)
        )

    def split_by_middle_hash(self, line):
        """
        Splits the line by middle occurence of hash (#).
        Returns tuple of Nones if there are not hashes at all (empty line).
        There is always an odd number of hashes (N in the regex, N in explanation, and one in the middle --> 2N+1).
        """
        hashes_count = line.count("#")

        if not hashes_count:
            return (None, None)

        regex       = None
        explanation = None
        i           = 0
        parts       = re.finditer(r"#", line)

        for part in parts:
            i += 1

            if i >= hashes_count / 2:
                regex       = line[ : part.start() ]
                explanation = line[ part.end() : ]

                break

        return (regex, explanation)

    def replace_by_patterns(self, string, substitutions):
        """
        Executes pattern substitution for given string and returnes modifed string.
        """
        for pattern, substitution in substitutions:
            string = re.sub(pattern, substitution, string)

        return string

    def build_html(self, explanation):
        """
        Creates the HTML structure for the explanation.
        """
        if not explanation:
            return None

        return """
            <body id=\"regex-explain-tip-popup\">
                <style>
                    %s
                </style>
                <div class=\"expander\">
                </div>
                %s
            </body>
        """ % (
            self.css,
            self.convert_lines_to_html(explanation.split("\n"))
        )

    def run(self, _):
        """
        Executes the plugin.
        """
        self.was_actual_rule = False

        message = self.build_html(
            self.get_explanation(
                self.get_selected_text()
            )
        )

        if message:
            self.view.show_popup(message,
                                 max_width  = 1200,
                                 max_height = 600)
