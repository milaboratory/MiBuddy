import copy


class AbstractParser(object):
    def get_parser_name(self):
        """
        Return parser name. Must be implemented by descendants
        :return: parser name
        """
        raise NotImplementedError("Should have implemented get_parser_name(self) method.")

    def on_traverse_down(self, fields, current_fields):
        """
        Calculate intermediate parser-specific results / actions on traverse-down pass, also provide additional fields
        for underlying parsers
        :param fields: aggregated dict of properties on the current level
        :param current_fields: set of fields emerged from current level
        :return: tuple (parser-specific result or action or None, additional_fields or {}) parser-specific result or
        None
        """
        return None, {}

    def aggregate(self, result1, result2):
        """
        Merge two parser-specific results
        :param result1:
        :param result2:
        :return: merged result
        """
        if isinstance(result1, list) and isinstance(result2, list):
            return result1 + result2

        if result1 or result2:
            raise NotImplementedError("Should have implemented aggregate(self, result1, result2) method.")

    def on_traverse_up(self, aggregated_result, fields, current_fields):
        """
        Return list of actions, having aggregated set of parser-specific results and information on current node
        :param aggregated_result:
        :param fields: aggregated dict of properties on the current level
        :param current_fields: set of fields emerged from current level
        :return: list of actions
        """
        if isinstance(aggregated_result, list):
            return aggregated_result
        elif aggregated_result:
            return [aggregated_result]
        else:
            return []


class Traverser:
    def __init__(self, *parsers, log_steps=False):
        self.log_steps = log_steps
        self.parsers = parsers

    def traverse(self, yam):
        """
        Main method of the class. Traverse input structure using provided set of parsers and return list of actions.
        :param yam: content of yaml file
        :return: list of actions
        """
        return self.traverse_down({"stage": "input"}, yam)[1]

    def calculate_results_on_traverse_up(self, results, fields_snapshots):
        """
        Produce actions from this node using on_traverse_up methods of individual parsers using intermediate
        parser-specific results aggregated for underlying branch
        :param results: dict of parser-specific results aggregated for underlying branch
        :param fields_snapshots: list of (fields, current_fields) tuples
        :return: list of actions
        """
        actions = []
        fsi = len(fields_snapshots)
        for parser in reversed(self.parsers):
            fsi -= 1
            parser_name = parser.get_parser_name()
            parser_actions = parser.on_traverse_up(results.get(parser_name, None), fields_snapshots[fsi][0],
                                                   fields_snapshots[fsi][1])
            if parser_actions:
                actions += parser_actions
        return actions

    def add_results_for_all_parsers(self, aggregated_results, result):
        """
        Aggregate two result maps using, parser-specific aggregation logic (aggregate method)
        :param aggregated_results: result map with previously aggregated results, new aggregation results will be
        written into it
        :param result: results form current execution step
        """
        for parser in self.parsers:
            parser_name = parser.get_parser_name()
            if parser_name in result:
                if parser_name in aggregated_results:
                    aggregated_results[parser_name] = parser.aggregate(aggregated_results[parser_name],
                                                                       result[parser_name])
                else:
                    aggregated_results[parser_name] = result[parser_name]

    @staticmethod
    def without_dot(d):
        if "." in d:
            d = copy.deepcopy(d)
            del d["."]
            return d
        else:
            return d

    def traverse_down(self, fields, raw_node):
        """
        Method to recursively traverse the tree
        :param fields: aggregated dictionary with aggregated upper-level fields
        :param raw_node: current node (map or array)
        :return:
        """
        if self.log_steps and (isinstance(raw_node, list) or isinstance(raw_node, dict)):
            print("current_map = " + str(fields))
            if isinstance(raw_node, dict):
                print("current_node = " + str(Traverser.without_dot(raw_node)))
            else:
                print("current_element = list")
            print("========")

        aggregated_results = {}
        aggregated_actions = []

        # Processing list node (YAML array node)
        if isinstance(raw_node, list):
            # Process all list elements one-by-one and collect resulting results and actions to pass them upwards
            for e in raw_node:
                # Recursive call of traverse_down for individual element
                (current_result, current_actions) = self.traverse_down(fields, e)
                # Aggregate intermediate parser-specific results into aggregated_results
                self.add_results_for_all_parsers(aggregated_results, current_result)
                # Add actions produced by current node to total list of actions
                aggregated_actions += current_actions

        # Processing dict node (YAML map node)
        elif isinstance(raw_node, dict):
            # Making deep copy of fields
            fields = copy.deepcopy(fields)
            current_fields = set()
            for key, value in raw_node.items():
                if key != '.':
                    # Adding fields form current node
                    fields[key] = value
                    # Saving information on which fields came from current node
                    current_fields.add(key)

            fields_snapshots = []
            # Pass current node to parser to calculate intermediate results using their on_traverse_down methods
            for parser in self.parsers:
                fields_snapshots += [(copy.deepcopy(fields), copy.deepcopy(current_fields))]
                parser_name = parser.get_parser_name()
                (current_result, additional_fields) = parser.on_traverse_down(fields, current_fields)

                if current_result:
                    aggregated_results[parser_name] = current_result

                if additional_fields:
                    for key, value in additional_fields.items():
                        fields[key] = value
                        current_fields.add(key)

                    if self.log_steps:
                        print("node updated by " + parser_name)
                        print("current_node = " + str(fields))
                        print("========")

            if '.' in raw_node:
                # Recursive call of traverse_down for individual element
                (current_result, current_actions) = self.traverse_down(fields, raw_node['.'])
                # Aggregate intermediate parser-specific results into aggregated_results
                self.add_results_for_all_parsers(aggregated_results, current_result)
                # Add actions produced by current node to total list of actions
                aggregated_actions += current_actions

            # Pass current node to parser to calculate resulting actions using information from current node and
            # aggregated object of intermediate results
            aggregated_actions += self.calculate_results_on_traverse_up(aggregated_results, fields_snapshots)

        return aggregated_results, aggregated_actions
