import copy


class AbstractParser(object):
    def get_parser_name(self):
        """
        Return parser name. Must be implemented by descendants
        :return: parser name
        """
        raise NotImplementedError("Should have implemented this")

    def on_traverse_down(self, current_map, current_key, current_element):
        """
        Calculate intermediate parser-specific results on traverse-down pass
        :param current_map: aggregated list of properties excluding current node
        :param current_key:
        :param current_element: current element
        :return: parser-specific result or None
        """
        return None

    def aggregate(self, result1, result2):
        """
        Merge two parser-specific results
        :param result1:
        :param result2:
        :return: merged result
        """
        if result1 or result2:
            raise NotImplementedError("Should have implemented this")

    def on_traverse_up(self, current_result, current_map, current_key, current_element):
        """
        Return list of actions, having aggregated set of parser-specific results and information on current node
        :param current_result:
        :param current_map:
        :param current_key:
        :param current_element:
        :return:
        """
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
        return self.traverse_down({}, "root", yam)[1]

    def calculate_results_on_traverse_down(self, current_map, current_key, current_element):
        """
        Execute on_traverse_down for all parsers for a given node and return results map {parser_name -> parser_result}
        :param current_map: aggregated list of properties excluding current node
        :param current_key:
        :param current_element: current element
        :return: results map {parser_name -> parser_result}
        """
        result = {}
        for parser in self.parsers:
            parser_name = parser.get_parser_name()
            current_result = parser.on_traverse_down(current_map, current_key, current_element)
            if current_result:
                result[parser_name] = parser.on_traverse_down(current_map, current_key, current_element)
        return result

    def calculate_results_on_traverse_up(self, current_results, current_map, current_key, current_element):
        """
        Produce actions from this node using on_traverse_up methods of individual parsers using intermediate
        parser-specific results aggregated for underlying branch
        :param current_results: map parser-specific results aggregated for underlying branch
        :param current_map: aggregated list of properties excluding current node
        :param current_key:
        :param current_element: current element
        :return:
        """
        actions = []
        for parser in self.parsers:
            parser_name = parser.get_parser_name()
            parser_actions = parser.on_traverse_up(current_results.get(parser_name, None), current_map, current_key,
                                                   current_element)
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

    def traverse_down(self, current_map, current_key, current_element):
        """
        Method to recursively traverse the tree
        :param current_map: aggregated list of properties excluding current node
        :param current_key:
        :param current_element: current element (map or array, or string in case of terminal yaml leaf)
        :return:
        """
        if self.log_steps and (isinstance(current_element, list) or isinstance(current_element, dict)):
            print("current_map = " + str(current_map))
            print("current_key = " + str(current_key))
            print("current_element = " + str(current_element))
            print("========")

        aggregated_results = {}
        aggregated_actions = []

        # Processing list node (YAML array node)
        if isinstance(current_element, list):
            # Process all list elements one-by-one and collect resulting results and actions to pass them upwards
            for e in current_element:
                # Recursive call of traverse_down for individual element
                (current_result, current_actions) = self.traverse_down(current_map, current_key, e)
                # Aggregate intermediate parser-specific results into aggregated_results
                self.add_results_for_all_parsers(aggregated_results, current_result)
                # Add actions produced by current node to total list of actions
                aggregated_actions += current_actions

        # Processing dict node (YAML map node)
        elif isinstance(current_element, dict):
            # Pass current node to parser to calculate intermediate results using their on_traverse_down methods
            aggregated_results = self.calculate_results_on_traverse_down(current_map, current_key, current_element)

            # Iterating over all nested maps/arrays and process them recursively
            for key, value in current_element.items():
                # Making deep copy of current_map
                new_current_map = copy.deepcopy(current_map)
                for key1, value1 in current_element.items():
                    if key1 != key:
                        # Adding parameters form current node
                        new_current_map[key1] = value1
                # Recursive call of traverse_down for individual element
                (current_result, current_actions) = self.traverse_down(new_current_map, key, value)
                # Aggregate intermediate parser-specific results into aggregated_results
                self.add_results_for_all_parsers(aggregated_results, current_result)
                # Add actions produced by current node to total list of actions
                aggregated_actions += current_actions

            # Pass current node to parser to calculate resulting actions using information from current node and
            # aggregated object of intermediate results
            aggregated_actions += self.calculate_results_on_traverse_up(aggregated_results,
                                                                        current_map, current_key,
                                                                        current_element)

        # In case of terminal leafs, both above ifs will fail, and aggregated_results = {}, aggregated_actions = []
        # Terminal leafs effectively will not be passed to any parsers, will just be ignored
        return aggregated_results, aggregated_actions
