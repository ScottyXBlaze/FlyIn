# *************************************************************************** #
#                                                                             #
#                                                        :::      ::::::::    #
#    base_state.py                                     :+:      :+:    :+:    #
#                                                    +:+ +:+         +:+      #
#    By: nyramana <nyramana@student.42antananariv  +#+  +:+       +#+         #
#                                                +#+#+#+#+#+   +#+            #
#    Created: 2026/06/11 18:44:39 by nyramana         #+#    #+#              #
#    Updated: 2026/06/11 18:45:22 by nyramana        ###   ########.fr        #
#                                                                             #
# *************************************************************************** #

from abc import ABC, abstractmethod
class State(ABC):
    @abstractmethod
    def run(self) -> None:
        pass
