# *************************************************************************** #
#                                                                             #
#                                                        :::      ::::::::    #
#    __init__.py                                       :+:      :+:    :+:    #
#                                                    +:+ +:+         +:+      #
#    By: nyramana <nyramana@student.42antananariv  +#+  +:+       +#+         #
#                                                +#+#+#+#+#+   +#+            #
#    Created: 2026/06/29 11:11:57 by nyramana         #+#    #+#              #
#    Updated: 2026/06/30 13:38:47 by nyramana        ###   ########.fr        #
#                                                                             #
# *************************************************************************** #

"""
Package that contains the rendering part of the program.

The class that handle the rendering part is the StateManager who can change
the screen and more things.
"""

from .screens import StateManager

__all__ = ["StateManager"]
