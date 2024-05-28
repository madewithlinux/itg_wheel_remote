import array
soundbar_power_on_off = array.array('H', [9028, 4502, 557, 602, 527, 603, 551, 579, 528, 602, 529, 601, 528, 603, 552, 577, 552, 578, 551, 1711, 530, 1732, 530, 1733, 554, 1709, 531, 1732, 529, 1732, 553, 1710, 530, 1733, 554, 577, 529, 601, 529, 601, 530, 601, 553, 577, 553, 578, 554, 1707, 555, 577, 551, 1711, 554, 1708, 553, 1710, 553, 1708, 530, 1733, 531, 1732, 554, 577, 553, 1704, 531])
soundbar_vol_up       = array.array('H', [9033, 4502, 580, 576, 555, 575, 556, 574, 556, 575, 556, 574, 556, 574, 556, 575, 555, 575, 555, 1707, 556, 1707, 555, 1707, 556, 1706, 556, 1707, 555, 1708, 555, 1708, 555, 1708, 555, 1708, 554, 576, 555, 576, 553, 577, 554, 577, 553, 552, 578, 1682, 579, 553, 579, 550, 555, 1709, 554, 1708, 554, 1708, 555, 1708, 555, 1708, 554, 577, 554, 1705, 554])
soundbar_vol_down     = array.array('H', [9031, 4499, 582, 575, 555, 575, 555, 575, 554, 576, 556, 574, 555, 576, 554, 575, 556, 575, 555, 1707, 554, 1708, 556, 1705, 557, 1706, 556, 1705, 557, 1706, 556, 1706, 556, 1705, 556, 1706, 554, 577, 555, 1706, 556, 575, 555, 575, 555, 575, 555, 1707, 554, 576, 554, 576, 554, 1707, 555, 575, 555, 1708, 555, 1685, 575, 1683, 579, 577, 552, 1678, 579])
soundbar_toggle_mute  = array.array('H', [9030, 4499, 581, 576, 556, 574, 554, 576, 553, 577, 553, 576, 555, 576, 554, 576, 555, 575, 554, 1706, 555, 1707, 555, 1706, 554, 1707, 555, 1707, 555, 1706, 553, 1708, 555, 1707, 554, 576, 554, 576, 553, 577, 553, 1707, 554, 577, 553, 577, 554, 1706, 555, 576, 554, 1706, 554, 1708, 553, 1707, 554, 578, 550, 1710, 553, 1707, 552, 579, 551, 1705, 553])

tv_power_on_off = array.array('H', [4540, 4491, 552, 1716, 528, 1716, 528, 1717, 528, 595, 527, 595, 528, 595, 527, 595, 527, 595, 526, 1718, 528, 1717, 527, 1717, 526, 597, 526, 597, 526, 596, 527, 595, 527, 596, 525, 597, 527, 1718, 500, 622, 524, 599, 525, 597, 523, 600, 501, 621, 501, 622, 501, 1743, 526, 596, 503, 1742, 528, 1716, 528, 1716, 526, 1718, 527, 1717, 528, 1716, 528])
tv_source       = array.array('H', [4516, 4514, 553, 1715, 528, 1715, 528, 1717, 526, 595, 528, 594, 527, 596, 527, 594, 553, 571, 526, 1717, 528, 1715, 527, 1716, 528, 595, 527, 595, 528, 595, 527, 595, 551, 572, 527, 1716, 528, 595, 527, 595, 528, 594, 528, 595, 526, 596, 527, 595, 526, 596, 528, 595, 526, 1717, 527, 1717, 526, 1717, 526, 1717, 525, 1718, 527, 1718, 525, 1719, 501])
tv_left         = array.array('H', [4490, 4541, 553, 1689, 554, 1688, 555, 1689, 553, 595, 527, 594, 527, 595, 527, 595, 527, 595, 526, 1718, 529, 1689, 552, 1692, 549, 596, 527, 595, 528, 595, 527, 594, 528, 594, 528, 1715, 528, 595, 526, 1717, 527, 595, 526, 596, 527, 1716, 527, 1693, 549, 596, 527, 595, 526, 1717, 526, 597, 525, 1718, 526, 1693, 549, 597, 526, 596, 526, 1717, 525])
tv_right        = array.array('H', [4517, 4514, 552, 1717, 525, 1717, 504, 1739, 503, 620, 502, 620, 502, 620, 501, 621, 502, 620, 502, 1741, 527, 1716, 503, 1741, 527, 595, 525, 597, 526, 595, 525, 598, 502, 620, 524, 597, 501, 1743, 501, 620, 501, 621, 526, 597, 524, 1694, 550, 1692, 526, 622, 500, 1718, 526, 622, 500, 1718, 526, 1717, 526, 1718, 527, 596, 525, 596, 527, 1717, 525])
tv_up           = array.array('H', [4512, 4521, 579, 1663, 580, 1662, 584, 1661, 557, 592, 528, 594, 504, 618, 527, 595, 528, 595, 528, 1716, 528, 1717, 527, 1716, 526, 596, 528, 595, 527, 595, 527, 595, 527, 596, 527, 596, 527, 595, 527, 595, 526, 596, 526, 597, 525, 1719, 525, 1721, 524, 597, 525, 1694, 550, 1693, 550, 1694, 550, 1694, 551, 1693, 551, 596, 501, 622, 500, 1718, 527])
tv_down         = array.array('H', [4517, 4515, 551, 1717, 504, 1740, 523, 1720, 505, 618, 502, 620, 501, 621, 502, 621, 501, 620, 502, 1742, 526, 1717, 528, 1716, 527, 596, 502, 620, 502, 619, 503, 620, 501, 622, 500, 1743, 524, 597, 511, 612, 502, 621, 501, 620, 502, 1742, 527, 1717, 503, 619, 517, 605, 502, 1741, 528, 1716, 503, 1740, 526, 1718, 526, 596, 525, 597, 526, 1718, 527])
tv_select       = array.array('H', [4490, 4539, 579, 1665, 580, 1665, 578, 1665, 578, 570, 555, 567, 529, 594, 554, 568, 555, 567, 530, 1689, 552, 1690, 553, 1692, 552, 594, 529, 594, 527, 595, 527, 595, 527, 595, 528, 595, 526, 596, 526, 596, 526, 1718, 524, 598, 524, 1720, 522, 1722, 500, 622, 502, 1719, 523, 1718, 525, 1718, 549, 598, 526, 1692, 552, 596, 525, 597, 525, 1692, 553])
tv_exit         = array.array('H', [4491, 4540, 578, 1663, 581, 1662, 580, 1663, 579, 570, 555, 568, 528, 593, 555, 567, 529, 594, 554, 1663, 580, 1664, 580, 1664, 580, 568, 555, 567, 530, 593, 529, 594, 528, 594, 529, 1715, 552, 569, 530, 1689, 578, 1665, 579, 569, 528, 1691, 553, 595, 527, 595, 527, 595, 529, 1691, 576, 570, 527, 595, 528, 1692, 551, 596, 526, 1696, 548, 1694, 550])
tv_hdmi_1       = array.array('H', [4542, 4549, 523, 1759, 524, 1737, 522, 1738, 521, 583, 522, 582, 522, 582, 498, 606, 521, 582, 498, 1738, 520, 1760, 499, 1739, 521, 604, 499, 584, 520, 607, 496])
tv_hdmi_2       = array.array('H', [4538, 4553, 520, 1760, 526, 1735, 498, 1763, 522, 582, 521, 581, 522, 583, 520, 583, 521, 583, 521, 1736, 499, 1761, 524, 1736, 498, 606, 498, 607, 497, 607, 522])
tv_hdmi_3       = array.array('H', [4517, 4577, 545, 1738, 497, 1761, 524, 1737, 521, 584, 520, 582, 521, 583, 521, 583, 497, 606, 498, 1761, 522, 1736, 523, 1737, 500, 605, 499, 605, 520, 584, 522])
