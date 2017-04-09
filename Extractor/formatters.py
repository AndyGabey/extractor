class JsonFormatter(object):
    def __init__(self, missing_val):
        self.missing_val = missing_val

    def header(self, cols):
        """Return json for header"""
        json_rows = ['{"header": [']

        header_row = []
        for col in cols:
            header_row.append('"{}"'.format(col))
        json_rows.append(','.join(header_row))
        json_rows.append('], "data": [')
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

    def rows(self, rows_data, last=False):
        for row_data in rows_data[:-1]:
            yield self.row(row_data)

        if last:
            yield self.row(rows_data[-1])[:-1]
        else:
            yield self.row(rows_data[-1])

    def footer(self):
        return ']}'
