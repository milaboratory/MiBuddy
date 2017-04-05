class MiXCRParser:
    def get_parser_name(self):
        return "mixcr"

    def on_traverse_down(self, fields, current_fields):
        # print("XCR: >>>>>>>>>>>>>>>>>>>>>")
        # print("XCR: Field values: " + str(fields))
        # print("XCR: Fields: " + str(current_fields))
        # print("XCR: >>>>>>>>>>>>>>>>>>>>>")
        return None, {}

    def on_traverse_up(self, aggregated_result, fields, current_fields):
        # print("XCR: <<<<<<<<<<<<<<<<<<<<<")
        # print("XCR: Field values: " + str(fields))
        # print("XCR: Fields: " + str(current_fields))
        # print("XCR: <<<<<<<<<<<<<<<<<<<<<")
        return []
