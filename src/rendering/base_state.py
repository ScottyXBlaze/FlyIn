# *************************************************************************** #
#                                                                             #
#                                                        :::      ::::::::    #
#    base_state.py                                     :+:      :+:    :+:    #
#                                                    +:+ +:+         +:+      #
#    By: nyramana <nyramana@student.42antananariv  +#+  +:+       +#+         #
#                                                +#+#+#+#+#+   +#+            #
#    Created: 2026/06/11 18:44:39 by nyramana         #+#    #+#              #
#    Updated: 2026/06/13 07:25:53 by nyramana        ###   ########.fr        #
#                                                                             #
# *************************************************************************** #

from abc import ABC, abstractmethod


class State(ABC):
    @abstractmethod
    def run(self, dt: float) -> int:
        """Run the program and return some signal."""
        pass

    @abstractmethod
    def reset(self) -> None:
        pass
