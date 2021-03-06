class JsonFormatter(object):
    def __init__(self):
        self.missing_val = None

    def header(self, cols):
        """Return json for header"""
        json_rows = ['{"header": [']

        header_row = []
        for col in cols:
            header_row.append('"{}"'.format(col))
        json_rows.append(','.join(header_row))
        json_rows.append('], ')
        return ''.join(json_rows)
    
    def row(self, row_data):
        """Return json for row *with final comma*"""
        json_row = []
        for cell in row_data:
            if cell is None:
                json_row.append('"{}"'.format(self.missing_val))
            else:
                json_row.append('"{}"'.format(cell))
        return '[' + ','.join(json_row) + '],'

    def units_row(self, units):
        """Return json for measurement units"""
        json_rows = ['"units": [']

        unit_row = []
        for unit in units:
            unit_row.append('"{}"'.format(unit))
        json_rows.append(','.join(unit_row))
        json_rows.append('], "data": [')
        return ''.join(json_rows)

    def rows(self, rows_data):
        """Return json for each row"""
        for row_data in rows_data:
            yield self.row(row_data)

    def error_message(self, error_type, msg, hint=None):
        json_error = ['{"']
        json_error.append(error_type)
        json_error.append('":"')
        json_error.append(msg)
        json_error.append('"')
        if hint:
            json_error.append(',"hint":"')
            json_error.append(hint)
            json_error.append('"')
        json_error.append('}')
        return ''.join(json_error)

    def error_footer(self, msg):
        json_error = ['],\n']
        json_error.append('"server_error": "{}"'.format(msg))
        json_error.append('}')
        return ''.join(json_error)

    def footer(self):
        """Close parenthesis"""
        return ']}'


class HtmlFormatter(object):
    def __init__(self):
        self.missing_val = None

    def header(self, cols):
        """Return html for header"""
        html_rows = ['<table border="1">']

        header_row = ['<thead><tr>']
        for col in cols:
            header_row.append('<th>{}</th>'.format(col))
        header_row.append('</tr>')
        html_rows.append(''.join(header_row))
        return '\n'.join(html_rows)

    def units_row(self, units):

        unit_row = ['<tr>']
        for col in units:
            unit_row.append('<th>{}</th>'.format(col))
        unit_row.append('</tr></thead>')
        return '\n'.join(unit_row)

    def row(self, row_data):
        """Return html for row"""
        html_row = ['<tr>']
        for cell in row_data:
            if cell is None:
                html_row.append('<td>{}</td>'.format(self.missing_val))
            else:
                html_row.append('<td>{}</td>'.format(cell))
        html_row.append('</tr>\n')
        return ''.join(html_row)

    def rows(self, rows_data):
        """Return html for each row"""
        for row_data in rows_data:
            yield self.row(row_data)

    def error_message(self, error_type, msg, hint=None):
        html = '<div id="error_type">{}: {}</div>'.format(error_type, msg)
        if hint:
            html += '\n<div id="hint">hint: {}</div>'.format(hint)
        return html

    def error_footer(self, msg):
        html_rows = ['</tbody>', '</table>']
        html_rows.append('<div id="server_error">server_error: {}</div>'.format(msg))
        return '\n'.join(html_rows)

    def footer(self):
        """Return final lines of html table"""
        html_rows = ['</tbody>', '</table>']
        return '\n'.join(html_rows)


class CsvFormatter(object):
    def __init__(self):
        self.missing_val = None

    def header(self, cols):
        """Return csv for header"""
        header_row = ','.join(cols)
        return header_row + '\n'

    def units_row(self, units):
        """ return CSV row for units"""
        return self.header(units) #Same as header row
    
    def row(self, row_data):
        """Return csv for row"""
        html_row = []
        for cell in row_data:
            if cell is None:
                html_row.append('{}'.format(self.missing_val))
            else:
                html_row.append('{}'.format(cell))
        row_str = ','.join(html_row)
        row_str = row_str + '\n'
        return row_str

    def rows(self, rows_data):
        """yield csv for each row"""
        for row_data in rows_data:
            yield self.row(row_data)

    def error_message(self, error_type, msg, hint=None):
        csv = 'ERROR: {}: {}'.format(error_type, msg)
        if hint:
            csv += '\nHINT: {}'.format(hint)

    def error_footer(self, msg):
        return 'ERROR: server_error: {}'.format(msg)

    def footer(self):
        """csv doesn't need a footer"""
        return ''
