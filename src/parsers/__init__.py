# *************************************************************************** #
#                                                                             #
#                                                        :::      ::::::::    #
#    __init__.py                                       :+:      :+:    :+:    #
#                                                    +:+ +:+         +:+      #
#    By: nyramana <nyramana@student.42antananariv  +#+  +:+       +#+         #
#                                                +#+#+#+#+#+   +#+            #
#    Created: 2026/06/07 19:54:09 by nyramana         #+#    #+#              #
#    Updated: 2026/06/07 19:54:09 by nyramana        ###   ########.fr        #
#                                                                             #
# *************************************************************************** #

"""Package that contain the parsers and the model for every entity."""

from .parsers import Parsers
from .printer import ModelPrinter

__all__ = ["Parsers", "ModelPrinter"]
