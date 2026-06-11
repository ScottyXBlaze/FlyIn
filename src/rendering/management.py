# *************************************************************************** #
#                                                                             #
#                                                        :::      ::::::::    #
#    management.py                                     :+:      :+:    :+:    #
#                                                    +:+ +:+         +:+      #
#    By: nyramana <nyramana@student.42antananariv  +#+  +:+       +#+         #
#                                                +#+#+#+#+#+   +#+            #
#    Created: 2026/06/11 11:07:10 by nyramana         #+#    #+#              #
#    Updated: 2026/06/11 11:08:32 by nyramana        ###   ########.fr        #
#                                                                             #
# *************************************************************************** #


class Management:
    def __init__(self) -> None:
        # list of drone by index, and in the drone list of position
        self.path: list[list[tuple[int, int]]] = []
