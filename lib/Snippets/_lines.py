# -*- coding: utf-8 -*-

# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝
#==================================================







# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝
#==================================================
def get_points_along_a_curve(curve, step=0.3):
    """ Function to get points along given Curve
    :param curve: Curve that will be tessellated.
    :param step:  approx. Step distance between points
    :return: list of Points along the curve."""

    # CONTAINER
    points = []

    # GET POINTS ALONG CURVE
    tessellation = curve.Tessellate()
    dist = 0

    pt = curve.GetEndPoint(0)
    for q in tessellation:

        if not points:
            points.append(pt)
            dist = 0.0

        else:
            dist += pt.DistanceTo(q)
            if dist >= step:
                points.append(q)
                dist = 0
        pt = q

    return points