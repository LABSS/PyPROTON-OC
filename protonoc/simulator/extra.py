# MIT License
#
# Copyright (c) 2019 LABSS(Francesco Mattioli, Mario Paolucci)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from __future__ import annotations
import numpy as np
import numba
import typing
from ast import literal_eval
if typing.TYPE_CHECKING:
    from .entities import Person
    from typing import List, Set, Dict, Union, Callable, Any, Tuple
    import pandas as pd
    import numpy

free_parameters = ["migration_on", "initial_agents", "num_ticks", "intervention",
                   "max_accomplice_radius", "number_arrests_per_year",
                   "number_crimes_yearly_per10k", "ticks_between_intervention",
                   "intervention_start", "intervention_end","num_oc_persons",
                   "num_oc_families", "education_modifier", "retirement_age",
                   "unemployment_multiplier", "nat_propensity_m",
                   "nat_propensity_sigma", "nat_propensity_threshold",
                   "facilitator_repression", "facilitator_repression_multiplier",
                   "likelihood_of_facilitators", "targets_addressed_percent",
                   "threshold_use_facilitators", "oc_embeddedness_radius",
                   "oc_boss_repression", "punishment_length", "constant_population"]

interventions_type = ["facilitators-strong", "facilitators", "students-strong", "students",
                      "disruptive-strong", "disruptive", "preventive-strong", "preventive",
                      "baseline"]


def find_neighb(netname: str, togo: int, found: Set, border: Set[Person]) -> Union[Set, Any]:
    """
    Find the nearest agent in @netname within range @togo, return a Set of agents
    :param netname: str, network name to search
    :param togo: int, search range
    :param found: Set,
    :param border: Set[Person]
    :return: Set,
    """

    found = found | border
    if togo == 0:
        return found
    #print_id(set().union(*[x.neighbors.get(netname) for x in border]))
    nextlayer = set().union(*[x.neighbors.get(netname) for x in border]) - found
    if not nextlayer:
        return found
    else:
        togo -= 1
        return find_neighb(netname, togo, found, nextlayer)


def wedding_proximity_with(ego: Person, pool: List[Person]) -> np.ndarray:
    """
    Given an agent and a pool of agents this function returns a list of proximities with ego. Careful not to shuffle it!
    :param ego: Person
    :param pool: list of Person objects
    :return: list, list of proximities with ego.
    """
    proximity = np.array([(ego.social_proximity(x) + (4 - abs(x.hobby - ego.hobby)) / 4) / 2
    for x in pool])
    if all([True for n in proximity if n <= 0]):
        proximity = np.ones(len(proximity))
    proximity /= np.sum(proximity)
    return proximity

def at_most(agentset: Union[List[Person], Set[Person]], n: int, rng_istance: numpy.random.default_rng) -> Union[List[Person], Set[Person]]:
    """
    Given an @agentset and an integer @n, this function returns the initial @agentset if there are
    less than @n agents, a subset of those agents of length @n if there are more than @n agents.
    :param agentset: Union[List[Person], Set[Person]]
    :param n: int
    :param rng_istance: numpy.random.default_rng
    :return: Union[List[Person], Set[Person]]
    """
    if len(agentset) < n:
        return agentset
    else:
        return list(rng_istance.choice(agentset, n, replace=False))


def weighted_n_of(n: int, agentset: Union[List[Person], Set[Person]],
                  weight_function: Callable, rng_istance: numpy.random.default_rng) -> List[Person]:
    """
    Given a set or List of agents @agentset an integer @n and a lambda function @weight_function.
    This function performs a weighted extraction, without replacing based on the lambda function.
    This procedure takes into account negative numbers and weights equal to zero.
    :param n: int
    :param agentset: Union[List[Person], Set[Person]]
    :param weight_function: Callable
    :param rng_istance: numpy.random.default_rng
    :return: List[Person]
    """
    p = [float(weight_function(x)) for x in agentset]
    for pi in p:
        if pi < 0:
            min_value = np.min(p)
            p = [i - min_value for i in p]
            break
    sump = sum(p)
    #if there are more zeros than n required in p
    if np.count_nonzero(p) < n:
        n = np.count_nonzero(p)
    #If there are only zeros
    if sump == 0:
        p = None
    else:
        p = [i/sump for i in p]
    #If the type is wrong
    if type(agentset) != list:
        agentset = list(agentset)
    return rng_istance.choice(agentset, int(n), replace=False, p=p)


def weighted_one_of(agentset: Union[List[Person], Set[Person]],
                    weight_function: Callable, rng_istance: numpy.random.default_rng) -> Any:
    return weighted_n_of(1, agentset, weight_function, rng_istance)[0]


def pick_from_pair_list(a_list_of_pairs: Union[List, np.ndarray],
                        rng_istance: numpy.random.default_rng) -> Any:
    """
    given a list of pairs, containing an object and a probability (e.g. [[object, p],[object, p]])
    return an object based on the probability(p)
    :param a_list_of_pairs:list, a list of pairs (e.g. [[object, p],[object, p]])
    :param rng_istance: numpy.random instance,
    :return: object
    """
    return weighted_one_of(a_list_of_pairs, lambda x: x[-1], rng_istance)[0]


def df_to_dict(df: pd.DataFrame, extra_depth: bool = False) -> Dict:
    """
    Based on the number of pandas DataFrame columns, transforms the dataframe into nested dictionaries as follows:
    df-columns = age, sex, education, p --> dict-keys = {age:{sex:[education, p]}}

    If extra_depth is True the transformation has an extra level of depth as follows:
    df-columns = age, sex, education, p --> dict-keys = {age:{sex:{education: p}}}

    This transformation ensures a faster access to the values using the dictionary keys.
    :param df: pd.DataFrame, the df to be transformed
    :param extra_depth: bool, if True gives an extra level of depth
    :return: Dict, a new dictionary
    """
    dic = dict()
    extra_depth_modifier = 0
    if extra_depth:
        extra_depth_modifier = 1
    if len(df.columns) + extra_depth_modifier == 2:
        for col in np.unique(df.iloc[:, 0]):
            dic[col] = df[df.iloc[:, 0] == col].iloc[:, 1].values
    if len(df.columns) + extra_depth_modifier == 3:
        for col in np.unique(df.iloc[:, 0]):
            dic[col] = df[df.iloc[:, 0] == col].iloc[:, 1:].values
    if len(df.columns) + extra_depth_modifier == 4:
        for col in np.unique(df.iloc[:, 0]):
            dic[col] = df[df.iloc[:, 0] == col].iloc[:, 1:]
        for key in dic:
            subdic = dict()
            for subcol in np.unique(dic[key].iloc[:, 0]):
                if extra_depth:
                    subdic[subcol] = dic[key][dic[key].iloc[:, 0] == subcol].iloc[:, 1:].values[0][0]
                else:
                    subdic[subcol] = dic[key][dic[key].iloc[:, 0] == subcol].iloc[:, 1:].values
            dic[key] = subdic
    return dic


def decide_conn_number(agents: Union[List, Set], max_lim: int, also_me: bool = True) -> int:
    """
    Given a set of agents decides the number of connections to be created between them based on a maximum number.
    :param agents: Union[List, Set], agents
    :param max_lim: int, an arbitrary maximum number
    :param also_me: bool, include caller
    :return: max_lim if the agents are more than max_lim otherwise returns the number of agents minus one.
    """
    if len(agents) <= max_lim:
        return len(agents) - 1 if also_me else len(agents)
    else:
        return max_lim


def df_to_lists(df: pd.DataFrame, split_row: bool = True) -> List:
    """
    This function transforms a pandas DataFrame into nested lists as follows:
    df-columns = age, sex, education, p --> list = [[age,sex],[education,p]]

    This transformation ensures a faster access to the values using the position in the list
    :param df: pandas df, the df to be transformed
    :param split_row: bool, default = True
    :return: list, a new list
    """
    output_list = list()
    if split_row:
        temp_list = df.iloc[:, :2].values.tolist()
        for index, row in df.iterrows():
            output_list.append([temp_list[index], [row.iloc[2], row.iloc[3]]])
    else:
        output_list = df.values.tolist()
    return output_list


def calculate_oc_status(co_offenders: List[Person]) -> None:
    """
    This procedure modify in-place the arrest_weigh attribute of the Person objects passed to co_offenders
    :param co_offenders: list, of Person object
    :return: None
    """
    for agent in co_offenders:
        agent.arrest_weight = agent.calculate_oc_member_position()
    min_score = np.min([agent.arrest_weight for agent in co_offenders])
    divide_score = np.mean([agent.arrest_weight - min_score for agent in co_offenders])
    for agent in co_offenders:
        if divide_score > 0:
            agent.arrest_weight = (agent.arrest_weight - min_score) / divide_score
        else:
            agent.arrest_weight = 1


def generate_collector_dicts(collect_agents) -> Union[Tuple[Dict, Dict], Dict]:
    """
    This returns two dictionaries consisting of as many key/value pairs as the elements
    contained within the @model_reporters, @agent_reporters parameters.
    :return: Tuple[Dict, Dict]
    """
    model_reporters = ["seed", "family_intervention", 'social_support', 'welfare_support',
                       'this_is_a_big_crime', 'good_guy_threshold', 'number_deceased',
                       'facilitator_fails', 'facilitator_crimes', 'crime_size_fails',
                       'number_born', 'number_migrants', 'number_weddings',
                       'number_weddings_mean', 'number_law_interventions_this_tick',
                       'correction_for_non_facilitators', 'number_protected_recruited_this_tick',
                       'people_jailed', 'number_offspring_recruited_this_tick', 'number_crimes',
                       'crime_multiplier', 'kids_intervention_counter', 'big_crime_from_small_fish',
                       'arrest_rate', 'migration_on', 'initial_agents', 'intervention',
                       'max_accomplice_radius', 'number_arrests_per_year', 'ticks_per_year',
                       'num_ticks', 'tick', 'ticks_between_intervention', 'intervention_start',
                       'intervention_end', 'num_oc_persons', 'num_oc_families',
                       'education_modifier', 'retirement_age', 'unemployment_multiplier',
                       'nat_propensity_m', 'nat_propensity_sigma', 'nat_propensity_threshold',
                       'facilitator_repression', 'facilitator_repression_multiplier',
                       'percentage_of_facilitators', 'targets_addressed_percent',
                       'threshold_use_facilitators', 'oc_embeddedness_radius',
                       'oc_boss_repression', 'punishment_length',
                       'constant_population', "number_crimes_yearly_per10k",
                       "number_crimes_committed_of_persons",  "current_oc_members",
                       "current_num_persons", 'criminal_tendency_mean', 'criminal_tencency_sd',
                       'age_mean', 'age_sd', 'education_level_mean', 'education_level_sd',
                       'num_crime_committed_mean', 'num_crime_committed_sd',
                       "crimes_committed_by_oc_this_tick", "current_prisoners", "employed",
                       "facilitators", "tot_friendship_link", "tot_household_link",
                       "tot_partner_link", "tot_offspring_link", "tot_criminal_link",
                       "tot_school_link", "tot_professional_link", "tot_sibling_link",
                       "tot_parent_link", "number_students", "number_jobs",
                       "likelihood_of_facilitators"]


    agent_reporters = ['unique_id', 'gender_is_male', 'prisoner', 'age', 'sentence_countdown',
                       'num_crimes_committed', 'num_crimes_committed_this_tick',
                       'education_level', 'max_education_level', 'wealth_level',
                       'job_level', 'propensity', 'oc_member', 'retired', 'number_of_children',
                       'facilitator', 'hobby', 'new_recruit', 'migrant', 'criminal_tendency',
                       'target_of_intervention', "cached_oc_embeddedness", 'sibling',
                       'offspring', 'parent', 'partner', 'household', 'friendship',
                       'criminal', 'professional', 'school']

    net_names = ['sibling', 'offspring', 'parent', 'partner', 'household', 'friendship',
                 'criminal', 'professional', 'school']

    model_reporters_dic = {key: key for key in model_reporters}
    agent_reporters_dic = {key: key if key not in net_names else lambda x: x.dump_net(key)
                                for key in agent_reporters }
    if collect_agents:
        return agent_reporters_dic, model_reporters_dic
    else:
        return model_reporters_dic

def convert_numerical(s: str) -> Union[int, float, str]:
    """
    This takes as argument a string, if this is composed of a number (integer or float)
    returns the number otherwise returns a string.
    :param s: str, the string to convert
    :return: Union[int, float, str]
    """
    if isinstance(s, str):
        try:
            val = literal_eval(s)
        except:
            val = s
    else:
        val = s
    if isinstance(val, float):
        if val.is_integer():
            return int(val)
        return val
    return val


def standardize_value(value: str) -> Union[str, int, float, None]:
    """
    This takes a string as a parameter and standardizes this value respecting
    the standard naming of the model.
    :param value: str
    :return: Union[str, int, float, None]
    """
    if any([ch.isdigit() for ch in value]):
        return convert_numerical(value)
    elif value == "\"none\"":
        return None
    elif value == "true":
        return True
    elif value == "false":
        return False
    elif "palermo" in value:
        return "palermo"
    elif "eindhoven" in value:
        return "eindhoven"
    else:
        return value.replace("\"", "")

def list_contains_problems(ego: Person, candidates:List[Person]) -> Union[bool, None]:
    """
    This procedure checks if there are any links between partners within the candidate pool.
    Returns True if there are, None if there are not. It is used during ProtonOc.setup_siblings
    procedure to avoid incestuous marriages.
    :param ego: Person, the agent
    :param candidates: Union[List[Person], Set[Person]], the candidates
    :return: Union[bool, None], True if there are links between partners, None otherwise.
    """
    all_potential_siblings = [ego] + ego.get_neighbor_list("sibling") + candidates + [sibling for candidate in
                                                                                      candidates for sibling in
                                                                                      candidate.neighbors.get(
                                                                                          'sibling')]
    for sibling in all_potential_siblings:
        if sibling.get_neighbor_list("partner") and sibling.get_neighbor_list("partner")[
            0] in all_potential_siblings:
            return True

#Numba functions
@numba.jit(nopython=True)
def _age(tick: int, birth_tick: int) -> int:
    return np.floor((tick - birth_tick) / 12)

if __name__ == "__main__":
    pass