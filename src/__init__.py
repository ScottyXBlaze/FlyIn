# *************************************************************************** #
#                                                                             #
#                                                        :::      ::::::::    #
#    __init__.py                                       :+:      :+:    :+:    #
#                                                    +:+ +:+         +:+      #
#    By: nyramana <nyramana@student.42antananariv  +#+  +:+       +#+         #
#                                                +#+#+#+#+#+   +#+            #
#    Created: 2026/06/29 11:32:14 by nyramana         #+#    #+#              #
#    Updated: 2026/06/30 13:32:08 by nyramana        ###   ########.fr        #
#                                                                             #
# *************************************************************************** #

"""
Package that contain every important code for the program.

this package stores the three main part of this project including the
algorithm, the parsers and the rendering to make import easy.
"""

from .algorithm import Algorithm
from .parsers import Parsers
from .rendering import StateManager

__all__ = ["Algorithm", "Parsers", "StateManager"]
