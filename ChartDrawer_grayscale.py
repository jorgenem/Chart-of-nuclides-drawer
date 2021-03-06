#!/usr/bin/env python3
"""
Copyright Krzysztof Miernik 2012
k.a.miernik@gmail.com 

Distributed under GNU General Public Licence v3

This script produces chart of nuclides in svg format from data
provided in xml document.

    usage: ChartDrawer.py [-h] [--names] [--halflives] [--magic] [--numbers]
                        [--z Z Z] [--n N N]
                        datafile outfile

    positional arguments:
    datafile     Input data base XML file (required)
    outfile      Output data SVG file (required)

    optional arguments:
    -h, --help   show this help message and exit
    --names      Show names
    --halflives  Show half-lives
    --magic      Show magic numbers
    --numbers    Show numbers along axis
    --z Z Z      Atomic number Z range (int), default: [0, 120]
    --n N N      Neutron number N range (int), default: [0, 180]

   The Nubase2xml.py script will generate the input xml file from Nubase format

   The NuBase ascii file can be downloaded from:
   http://amdc.in2p3.fr/nubase/nubtab03.asc

   Please note that the database is old (2003) so many values are outdated.
   As soon as expected NuBase2013 is released the Nubase2xml script will 
   be updated to parse new data format.

   The generated chart of nuclides is following (but not precisely) the format
   of Karlsruher Chart of Nuclides. The nuclides are coded with colors according to
   primary decay mode:
   Black - stable
   Yellow - Alpha
   Red - B+/EC
   Blue - B-
   Green - fission
   Orange - proton / two-proton emission
   Violet - cluster emission
   Light blue - neutron / two-neutron emission

   Secondary decay mode is indicated by triangle. A large triangle is used if
   secondary decay mode branching is larger then 5%. Otherwise small triangle is
   used (likewise for tertiary decay mode).

   A Nuclide class provides parser to read data from NuBase ascii file or xml
   document. Note that some information is not being used on the chart 
   (e.g. mass of nuclides, isomeric states), but is present in the data base.
   The Nuclide class can easyli used to write scripts using these informations 
   as well.
"""

import sys
import argparse
import re
import xml.dom.minidom
from Nuclide import *

# Definition of colors used for decay modes
COLORS = { 'is': '#000000',
           'b-': '#62aeff',
           '2b-': '#62aeff',
           'b+': '#ff7e75',
           'ec': '#ff7e75',
           '2ec': '#ff7e75',
           'a' : '#fffe49',
           'sf': '#5cbc57',
           'p' : '#ffa425',
           '2p': '#ffa425', 
           'n' : '#9fd7ff',
           '2n': '#9fd7ff',
           'it': '#ffffff',
           'cluster': '#a564cc',
           '?': '#cccccc' }

def color_to_grayscale_hex(color_hex_string):
    """
    JEM: Converts a hex color to grayscale by averaging the color
    """
    r_str, g_str, b_str = color_hex_string[1:3], color_hex_string[3:5], color_hex_string[5:7]
    r, g, b = int(r_str, 16), int(g_str, 16), int(b_str, 16)
    gray = 0.2989 * r + 0.5870 * g + 0.1140 * b
    gray = int(gray)

    def dec_to_hex(dec_int):
        # Very hacky code, sorry
        # Assumes dec_int <= 255
        char1 = hex(dec_int // 16)[2:3]
        char2 = hex(dec_int % 16)[2:3]

        return char1+char2

    gray_hex_string = "#"+3*dec_to_hex(gray)
    return gray_hex_string


for key, value in COLORS.items():
    COLORS[key] = color_to_grayscale_hex(value)




# List of nuclei that have Oslo measurements.
# Comment indicates upbend status: "yes", "no" or "unclear"
oslo_nuclides = {
    "La138": Nuclide(A=138, Z=57, comment="yes"),
    "Zr91": Nuclide(A=91, Z=40, comment="yes"),
    "Zr92": Nuclide(A=92, Z=40, comment="yes"),
    "Fe56": Nuclide(A=56, Z=26, comment="yes"),
    "Fe57": Nuclide(A=57, Z=26, comment="yes"),
    "V50": Nuclide(A=50, Z=23, comment="yes"),
    "V51": Nuclide(A=51, Z=23, comment="yes"),
    "Mo93": Nuclide(A=93, Z=42, comment="yes"),
    "Mo94": Nuclide(A=94, Z=42, comment="yes"),
    "Mo95": Nuclide(A=95, Z=42, comment="yes"),
    "Mo96": Nuclide(A=96, Z=42, comment="yes"),
    "Mo97": Nuclide(A=97, Z=42, comment="yes"),
    "Mo98": Nuclide(A=98, Z=42, comment="yes"),
    "Sc43": Nuclide(A=43, Z=21, comment="yes"),
    "Sc44": Nuclide(A=44, Z=21, comment="yes"),
    "Sc45": Nuclide(A=45, Z=21, comment="yes"),
    "Ti44": Nuclide(A=44, Z=22, comment="yes"),
    "Ti45": Nuclide(A=45, Z=22, comment="yes"),
    "Ti46": Nuclide(A=46, Z=22, comment="yes"),
    "Cd105": Nuclide(A=105, Z=48, comment="yes"),
    "Cd106": Nuclide(A=106, Z=48, comment="yes"),
    "Y89": Nuclide(A=89, Z=39, comment="yes"),
    "Y90": Nuclide(A=90, Z=39, comment="yes"),
    "Ge73": Nuclide(A=73, Z=32, comment="yes"),
    "Ge74": Nuclide(A=74, Z=32, comment="yes"),
    "Ge76": Nuclide(A=76, Z=32, comment="yes"),
    "Sm151": Nuclide(A=151, Z=62, comment="yes"),
    "Sm153": Nuclide(A=153, Z=62, comment="yes"),
    "Ni59": Nuclide(A=59, Z=28, comment="yes"),
    "Ni60": Nuclide(A=60, Z=28, comment="yes"),
    "Ni63": Nuclide(A=63, Z=28, comment="yes"),
    "Ni65": Nuclide(A=65, Z=28, comment="yes"),
    "Ni69": Nuclide(A=69, Z=28, comment="yes"),
    "Ni69": Nuclide(A=69, Z=28, comment="yes"),
    "Ni70": Nuclide(A=70, Z=28, comment="yes"),
    # "": Nuclide(A=, Z=, comment="yes"),

    "Dy160": Nuclide(A=160, Z=66, comment="no"),
    "Dy161": Nuclide(A=161, Z=66, comment="no"),
    "Dy162": Nuclide(A=162, Z=66, comment="no"),
    "Dy163": Nuclide(A=163, Z=66, comment="no"),
    "Dy164": Nuclide(A=163, Z=66, comment="no"),
    "Er166": Nuclide(A=166, Z=68, comment="no"),
    "Er167": Nuclide(A=167, Z=68, comment="no"),
    "Yb170": Nuclide(A=170, Z=70, comment="no"),
    "Yb171": Nuclide(A=171, Z=70, comment="no"),
    "Yb172": Nuclide(A=172, Z=70, comment="no"),
    "Sm148": Nuclide(A=148, Z=62, comment="no"),
    "Sm149": Nuclide(A=149, Z=62, comment="no"),
    "Sn116": Nuclide(A=116, Z=50, comment="no"),
    "Sn117": Nuclide(A=117, Z=50, comment="no"),
    "Sn118": Nuclide(A=118, Z=50, comment="no"),
    "Sn119": Nuclide(A=119, Z=50, comment="no"),
    "Sn121": Nuclide(A=121, Z=50, comment="no"),
    "Sn122": Nuclide(A=122, Z=50, comment="no"),
    "Cd111": Nuclide(A=111, Z=48, comment="no"),
    "Cd112": Nuclide(A=112, Z=48, comment="no"),
    "Th231": Nuclide(A=231, Z=90, comment="no"),
    "Th232": Nuclide(A=232, Z=90, comment="no"),
    "Th233": Nuclide(A=233, Z=90, comment="no"),
    "Pa232": Nuclide(A=232, Z=91, comment="no"),
    "Pa233": Nuclide(A=233, Z=91, comment="no"),
    "U237": Nuclide(A=237, Z=92, comment="no"),
    "U238": Nuclide(A=238, Z=92, comment="no"),
    "U239": Nuclide(A=239, Z=92, comment="no"),
    "Pd106": Nuclide(A=106, Z=46, comment="no"),
    "Pd107": Nuclide(A=107, Z=46, comment="no"),
    "Pd108": Nuclide(A=108, Z=46, comment="no"),
    "Np238": Nuclide(A=238, Z=93, comment="no"),
    "Pu243": Nuclide(A=243, Z=94, comment="no"),
    # "": Nuclide(A=, Z=, comment="no"),


    "Pb205": Nuclide(A=205, Z=82, comment="unclear"),
    "Pb206": Nuclide(A=206, Z=82, comment="unclear"),
    "Pb207": Nuclide(A=207, Z=82, comment="unclear"),
    "Pb208": Nuclide(A=208, Z=82, comment="unclear"),
    "Pd105": Nuclide(A=105, Z=46, comment="unclear"),
    "La139": Nuclide(A=139, Z=57, comment="unclear"),
    "La140": Nuclide(A=140, Z=57, comment="unclear"),
    "Mo92": Nuclide(A=92, Z=42, comment="unclear"),
    # "": Nuclide(A=, Z=, comment="unclear"),

}


    


FONT_COLOR_DARK = '#000000'
FONT_COLOR_BRIGHT = '#aaaaaa'

# Size of rectangle in pixels
SIZE_SHAPE = 30
# Size of margin between rectangles in pixels
SIZE_GAP = 2 
# Total size of one nuclid with margin
SIZE_FIELD = SIZE_SHAPE + SIZE_GAP
# Font size used for element name
SIZE_FONT = 7 
# Font size used for half-life
SIZE_FONT_HL = 5 

MAGIC_NUMBERS = [2, 8, 20, 28, 50, 82, 126]

def load_xml_nuclear_table(datafile, n_range, z_range,
                           n_limits = [None, None], z_limits = [None, None]):
    """Loads data from nuclear table in xml format. Returns list of
    Nuclide objects
    """
    # Make high and low limit oposite
    # Later each point is checked against:
    # n_limits[0] = N if N < n_limits[0]
    # n_limits[1] = N if N > n_limits[1]
    # (Z likewise)
    # So oposite limit here forces first point to set 
    # reasonable limits without loosing any data point
    n_limits[0] = n_range[1]
    n_limits[1] = n_range[0]

    z_limits[0] = z_range[1]
    z_limits[1] = z_range[0]

    try:
        dom = xml.dom.minidom.parse(datafile)
    except (EnvironmentError, xml.parsers.expat.ExpatError) as err:
        print("{0}: import error: {1}".format(datafile, err))
        return None

    data = []
    for nuclide in dom.getElementsByTagName("nuclide"):
        try:
            A = int(nuclide.getAttribute('A'))
            Z = int(nuclide.getAttribute('Z'))
            N = A - Z

            if not(n_range[0] <= N <= n_range[1] and 
                z_range[0] <= Z <= z_range[1]):
                continue
            elif N > n_range[1] and Z > z_range[1]:
                break

            if N < n_limits[0]:
                n_limits[0] = N
            if N > n_limits[1]:
                n_limits[1] = N
            if Z < z_limits[0]:
                z_limits[0] = Z
            if Z > z_limits[1]:
                z_limits[1] = Z

            isotope = NuclideXml(Z, A, nuclide)
            data.append(isotope)
        except (ValueError, LookupError) as err:
            print("{0}: import error: {1}".format(datafile, err))
            return False
    return data


# JEM additions:
def _draw_star(layer, position, color, name):
    """Draws star """
    x = position[0]
    y = position[1]
    star = svg.createElement("polygon")
    star.setAttribute("id", '{}'.format(name))
    star.setAttribute("stroke", "#000000")
    star.setAttribute("stroke-width", "0.0")
    star.setAttribute("stroke-linejoin", "bevel")
    star.setAttribute("fill", color)
    star.setAttribute("x", str(position[0]))
    star.setAttribute("y", str(position[1]))
    scalefactor = 3.0
    star.setAttribute( "points", 
                           "{}, {} {}, {} {}, {} {}, {} {}, {}".format(x-SIZE_SHAPE/2 +100/scalefactor,y-SIZE_SHAPE/1.4+10/scalefactor, x-SIZE_SHAPE/2 +40/scalefactor,y-SIZE_SHAPE/1.4+198/scalefactor, x-SIZE_SHAPE/2 +190/scalefactor,y-SIZE_SHAPE/1.4+78/scalefactor, x-SIZE_SHAPE/2 +10/scalefactor, y-SIZE_SHAPE/1.4+78/scalefactor, x-SIZE_SHAPE/2 +160/scalefactor, y-SIZE_SHAPE/1.4+198/scalefactor))
    layer.appendChild(star)

def _draw_diamond(layer, position, color, name):
    """Draws diamond """
    # Take coordinates x and y to be center of the current nucleus rectangle
    x = position[0] + SIZE_SHAPE/2
    y = position[1] + SIZE_SHAPE/2
    diamond = svg.createElement("polygon")
    diamond.setAttribute("id", '{}'.format(name))
    diamond.setAttribute("stroke", "#000000")
    diamond.setAttribute("stroke-width", "0.0")
    diamond.setAttribute("stroke-linejoin", "bevel")
    diamond.setAttribute("fill", color)
    diamond.setAttribute("x", str(position[0]))
    diamond.setAttribute("y", str(position[1]))
    dwidth_x = 1.7*SIZE_SHAPE/2 # Distance from diamond center to horizontal corner
    dwidth_y = 2.3*SIZE_SHAPE/2  # and to vertical center
    diamond.setAttribute( "points", 
                           "{}, {} {}, {} {}, {} {}, {}".format(x-dwidth_x, y, x, y+dwidth_y, x+dwidth_x, y, x, y-dwidth_y))
    layer.appendChild(diamond)

def _draw_circle(layer, position, color, name):
    """Draws circle """
    x = position[0]
    y = position[1]
    circle = svg.createElement("circle")
    circle.setAttribute("id", '{}'.format(name))
    # circle.setAttribute("stroke", "#000000")
    # circle.setAttribute("stroke-width", "0.0")
    # circle.setAttribute("stroke-linejoin", "bevel")
    circle.setAttribute("fill", color)
    circle.setAttribute("cx", str(x+SIZE_SHAPE/2))
    circle.setAttribute("cy", str(y+SIZE_SHAPE/2))
    scalefactor = 1.2
    circle.setAttribute("r", str(SIZE_SHAPE/scalefactor))
    layer.appendChild(circle)

# END JEM additions



def _draw_rectangle(layer, position, color, name):
    """Draws rectangle (basic nuclide on map) position is
    given for left top corner """
    x = position[0]
    y = position[1]
    rectangle = svg.createElement("rect")
    rectangle.setAttribute("id", '{}'.format(name))
    rectangle.setAttribute("width", str(SIZE_SHAPE))
    rectangle.setAttribute("height", str(SIZE_SHAPE))
    rectangle.setAttribute("stroke", "#000000")
    rectangle.setAttribute("stroke-width", "0.05")
    rectangle.setAttribute("fill", color)
    rectangle.setAttribute("x", str(position[0]))
    rectangle.setAttribute("y", str(position[1]))
    layer.appendChild(rectangle)

def _draw_triangle(layer, position, color, name, corner = 'rb'):
    """Draws triangle (half-rectangle), position is given
    for left top corner of rectangle, triangle is drawn in
    right bottom corner"""
    x = position[0]
    y = position[1]
    triangle = svg.createElement("polygon")
    triangle.setAttribute("id", '{}'.format(name))
    triangle.setAttribute("stroke", "#000000")
    triangle.setAttribute("stroke-width", "0.0")
    triangle.setAttribute("stroke-linejoin", "bevel")
    triangle.setAttribute("fill", color)
    triangle.setAttribute("x", str(position[0]))
    triangle.setAttribute("y", str(position[1]))
    if corner == 'lt':
        x1 = x + 0.25
        y1 = y + SIZE_SHAPE - 0.25
        x2 = x1 
        y2 = y + 0.25
        x3 = x + SIZE_SHAPE - 0.25
        y3 = y2 
    else:
        #default right bottom corner
        x1 = x + 0.25
        y1 = y + SIZE_SHAPE - 0.25
        x2 = x + SIZE_SHAPE - 0.25
        y2 = y + 0.25
        x3 = x2 
        y3 = y1 
    triangle.setAttribute( "points", 
                           "{},{} {},{} {},{}".format(x1, y1, x2, y2, x3, y3))
    layer.appendChild(triangle)

def _draw_small_triangle(layer, position, color, name, corner = 'rb'):
    """Draws small triangle in the corner of rectangle,
    position is left top corner of rectangle"""
    x = position[0]
    y = position[1]
    small_triangle = svg.createElement("polygon")
    small_triangle.setAttribute("id", '{}'.format(name))
    small_triangle.setAttribute("stroke", "#000000")
    small_triangle.setAttribute("stroke-width", "0.0")
    small_triangle.setAttribute("stroke-linejoin", "bevel")
    small_triangle.setAttribute("fill", color)
    small_triangle.setAttribute("x", str(position[0]))
    small_triangle.setAttribute("y", str(position[1]))
    if corner == 'lt':
        x1 = x + 0.25
        y1 = y +  1 / 3 * SIZE_SHAPE
        x2 = x1 
        y2 = y + 0.25
        x3 = x + 1 / 3 * SIZE_SHAPE
        y3 = y2 
    elif corner == 'rt':
        x1 = x + 2 / 3 * SIZE_SHAPE
        y1 = y + 0.25
        x2 = x + SIZE_SHAPE - 0.25
        y2 = y1
        x3 = x2
        y3 = y + 1 / 3 * SIZE_SHAPE 
    else:
        # default right bottom case
        x1 = x + SIZE_SHAPE * 2 / 3
        y1 = y + SIZE_SHAPE - 0.25
        x2 = x + SIZE_SHAPE - 0.25
        y2 = y1
        x3 = x2
        y3 = y + SIZE_SHAPE * 2 / 3
    small_triangle.setAttribute(
            "points",
            "{},{} {},{} {},{}".format(x1, y1, x2, y2, x3, y3))
    layer.appendChild(small_triangle)


def _draw_text(layer, position, font_color, font_size, text):
    """Draws text"""
    x = position[0]
    y = position[1]
    text_node = svg.createTextNode(text)

    text_el = svg.createElement("text")
    text_el.appendChild(text_node)
    text_el.setAttribute("text-anchor", "middle")
    text_el.setAttribute("font-family", "sans")
    text_el.setAttribute(
                "style", 
                "font-size:{}px; fill:{}".format(font_size, font_color))
    text_el.setAttribute("x", '{0:.2f}'.format(x))
    text_el.setAttribute("y", '{}'.format(y))
    layer.appendChild(text_el)

def _draw_line(layer, begin, end, name):
    """Draws line, begin and end should be a lists of [x,y]
    coordinates of line"""
    x1 = begin[0]
    y1 = begin[1]
    x2 = end[0]
    y2 = end[1]
    line = svg.createElement("line")
    line.setAttribute("id", str(name))
    line.setAttribute("stroke", "#000000")
    line.setAttribute("stroke-width", "8.0")
    line.setAttribute("x1", str(x1))
    line.setAttribute("y1", str(y1))
    line.setAttribute("x2", str(x2))
    line.setAttribute("y2", str(y2))
    layer.appendChild(line)

def draw_nuclide(nuclide, layers, position, args):
    """ Draws nuclide data, including primary and secondary decay modes,
        and name of nuclide """

    # List of accepted basic decay modes, primary color is chosen on 
    # that basis. A '?' mode is for placeholders.
    basic_decay_modes = ['is', 'a', 'b-', 'b+',
                           'ec', 'p', '2p', 'sf', 
                           'n', '2n', '2ec', '2b-']
    # This reg ex. matches cluster emission marked by isotopic name
    # it matches names starting by at excatly two digits and
    # ending with letter(s). Remember that all decay modes are lower cased!
    # Cluster decays are only secondary or tertiary
    cluster_re = r'[0-9]{2}([a-z]+)$'

    # First decay mode should be largest and should match one
    # of basic decay modes
    if nuclide.decay_modes[0]['mode'] in basic_decay_modes:
        primary_color = COLORS[nuclide.decay_modes[0]['mode']]
    elif nuclide.decay_modes[0]['mode'] == '?' and args.unknown:
        primary_color = COLORS['?']
    else:
        # Order of basic and secondary decay modes is not kept well in NWC data
        # eg. sometimes B+p is given before B+
        # We will swap two element so any basic mode comes first
        if len(nuclide.decay_modes) > 1:
            i = 0
            for i in range(1, len(nuclide.decay_modes)):
                if nuclide.decay_modes[i]['mode'] in basic_decay_modes:
                    nuclide.decay_modes[0], nuclide.decay_modes[i] = nuclide.decay_modes[i], nuclide.decay_modes[0]
                    primary_color = COLORS[nuclide.decay_modes[0]['mode']]
                    break
            else:
                return
        else:
            return

    
    # Ommit p-unstable and n-unstable (this information
    # is in half-life)
    if nuclide.half_life['value'].find('unstable') >= 0:
        return

    # If there is more decay modes, and if at least one matches
    # basic decay modes, a secondary color will be used
    # Large triangle is used for modes with branching > 5%
    # but not for long lived nuclides (quasi-stable)
    # small triangle for other
    # If large triangle is used, a tertiary decay mode might
    # be indicated with small triangle
    secondary_size = None
    tertiary_size  = None
    if len(nuclide.decay_modes) > 1:
        for i in range(1, len(nuclide.decay_modes)):
            if nuclide.decay_modes[i]['mode'] in basic_decay_modes:
                secondary_color = COLORS[nuclide.decay_modes[i]['mode']]
                try:
                    if ( float(nuclide.decay_modes[i]['value']) > 5.0 and
                         primary_color != COLORS['is'] ) :
                        secondary_size = 'large'
                    else:
                        secondary_size = 'small'
                    break
                except ValueError:
                    secondary_size = 'small'
            elif re.search(cluster_re, nuclide.decay_modes[i]['mode']) is not None:
                secondary_size = 'small'
                secondary_color = COLORS['cluster']
                break

        if ( len(nuclide.decay_modes) > 2 and
             ( secondary_size == 'large' or
               (secondary_size == 'small' and primary_color == COLORS['is'])) ):
            for i in range(2, len(nuclide.decay_modes)):
                if nuclide.decay_modes[i]['mode'] in basic_decay_modes:
                    tertiary_color = COLORS[nuclide.decay_modes[i]['mode']]
                    tertiary_size  = 'small'
                    break
                elif re.search(cluster_re, 
                               nuclide.decay_modes[i]['mode']) is not None:
                    tertiary_size = 'small'
                    tertiary_color = COLORS['cluster']
                    break

    _draw_rectangle(layers[0], position,
                    primary_color, '{}0'.format(nuclide))

    if secondary_size == 'large':
        if secondary_color == COLORS['a']:
            corner = 'lt'
        elif ( secondary_color == COLORS['b+'] and 
               primary_color != COLORS['a'] and 
               primary_color != COLORS['p'] ) :
            corner = 'lt'
        else:
            corner = 'rb'
        _draw_triangle(layers[1], position, secondary_color,
                       '{}1'.format(nuclide), corner)
    elif secondary_size == 'small':
        if secondary_color == COLORS['a']:
            corner = 'lt'
        elif ( secondary_color == COLORS['b+'] and 
               primary_color != COLORS['a'] and 
               primary_color != COLORS['p'] ) :
            corner = 'lt'
        elif secondary_color == COLORS['cluster']:
            corner = 'rt'
        else:
            corner = 'rb'
        _draw_small_triangle(layers[1], position, secondary_color,
                             '{}1'.format(nuclide), corner)

    if tertiary_size == 'small':
        if tertiary_color == COLORS['a']:
            corner = 'lt'
        elif ( tertiary_color == COLORS['b+'] and 
               primary_color != COLORS['a'] and 
               secondary_color != COLORS['a']) :
            corner = 'lt'
        elif tertiary_color == COLORS['cluster']:
            corner = 'rt'
        else:
            corner = 'rb'
        _draw_small_triangle(layers[1], position, tertiary_color,
                             '{}2'.format(nuclide), corner)

    font_color = FONT_COLOR_BRIGHT if primary_color == COLORS['is'] else FONT_COLOR_DARK
    if args.names:
        element_name = nuclide.element + " " + str(nuclide.A) 

        tx = position[0] + SIZE_SHAPE / 2 
        ty = position[1] + SIZE_GAP + 1.25 * SIZE_FONT

        _draw_text(layers[3], [tx, ty], font_color, SIZE_FONT, element_name)

    if (args.halflives and not(nuclide.half_life['extrapolated'] == 'True')):
        # For stable and quasi-stable nuclide print isotopic abundance
        # for unstable - half live
        if primary_color != COLORS['is']:
            half_life_string = nuclide.half_life['value'] 
            sci_re = r'^[-+]?[0-9]*\.?[0-9]+([eE]+[-+]?[0-9]+)$'
            if re.search(sci_re, half_life_string) is not None:
                try:
                    hl = float(half_life_string)
                    half_life_string = '{0:.1e}'.format(hl)
                except TypeError:
                    pass
            if nuclide.half_life['value'] != '?':
                half_life_string +=  ' ' + nuclide.half_life['unit']
                if nuclide.half_life['relation'] != '=':
                    half_life_string = nuclide.half_life['relation'] + ' ' + half_life_string
        else:
            half_life_string = nuclide.decay_modes[0]['value']

        # text position center
        tx = position[0] + SIZE_SHAPE / 2
        ty = position[1] + SIZE_SHAPE - 1.5 * SIZE_FONT_HL

        _draw_text(layers[3], [tx, ty], font_color, SIZE_FONT_HL,
                   half_life_string)


def draw_magic_lines(layers, n_magic, z_magic,
                             n_limits, z_limits, size):
    for N, limits in n_magic.items():
        x1 = (N - n_limits[0] + 1) * SIZE_FIELD + SIZE_GAP / 2
        x2 = x1
        y1 = size[1] - (limits[1] - z_limits[0] + 2) * SIZE_FIELD - SIZE_GAP / 2
        y2 = size[1] - (limits[0] - z_limits[0] + 1) * SIZE_FIELD - SIZE_GAP / 2
        _draw_line(layers[2], [x1, y1], [x2, y2], "{}n0".format(N))
        x1 = (N - n_limits[0] + 2) * SIZE_FIELD + SIZE_GAP / 2
        x2 = x1
        _draw_line(layers[2], [x1, y1], [x2, y2], "{}n1".format(N))

    for Z, limits in z_magic.items():
        x1 = (limits[0] - n_limits[0] + 1) * SIZE_FIELD + SIZE_GAP / 2 
        x2 = (limits[1] - n_limits[0] + 2) * SIZE_FIELD + SIZE_GAP / 2
        y1 = size[1] - (Z - z_limits[0] + 2) * SIZE_FIELD - SIZE_GAP / 2
        y2 = y1
        _draw_line(layers[2], [x1, y1], [x2, y2], "{}z0".format(Z))
        y1 = size[1] - (Z - z_limits[0] + 1) * SIZE_FIELD - SIZE_GAP / 2
        y2 = y1
        _draw_line(layers[2], [x1, y1], [x2, y2], "{}z1".format(Z))

def draw_numbers(layers, shape, n_limits, z_limits, size):
    for n in range(0, n_limits[1] - n_limits[0] + 1):
        if (n + n_limits[0]) % 2 == 0 and (n + n_limits[0] > 0):
            z_first = 0
            while ( not(shape[n][z_first]) and 
                    z_first < z_limits[1] - z_limits[0] + 1 ):
                z_first += 1
            x = (n + 1) * SIZE_FIELD + SIZE_GAP + SIZE_SHAPE / 2 
            y = size[1] - (z_first + 1) * SIZE_FIELD + SIZE_GAP + 1.25 * SIZE_FONT
            _draw_text(layers[3], [x, y], '#000000', 
                       SIZE_FONT * 1.5, str(n + n_limits[0]))
    for z in range(0, z_limits[1] - z_limits[0] + 1):
        if (z + z_limits[0] % 2) % 2 == 0 and (z + z_limits[0] > 0):
            n_first = 0
            while ( not(shape[n_first][z]) and 
                    n_first < n_limits[1] - n_limits[0] + 1 ):
                n_first += 1
            x = (n_first) * SIZE_FIELD + SIZE_SHAPE / 2 + 3 * SIZE_GAP
            y = size[1] - (z + 2) * SIZE_FIELD + SIZE_SHAPE / 2 +2 * SIZE_GAP
            _draw_text(layers[3], [x, y], '#000000', 
                       SIZE_FONT * 1.5, str(z + z_limits[0]))



def draw_Oslo_upbend_nuclei(nuclide, layers, position, args):
    """ Draws nuclide data, including primary and secondary decay modes,
        and name of nuclide """

    primary_color = None
    if nuclide.comment == "yes":
        primary_color = "#FFCD16"
        _draw_star(layers[3], position,
                        primary_color, '{}0'.format(nuclide))
    elif nuclide.comment == "no":
        primary_color = "#B23914"
        _draw_circle(layers[3], position,
                        primary_color, '{}0'.format(nuclide))
    elif nuclide.comment == "unclear":
        primary_color = "#3A4FCC"
        _draw_diamond(layers[3], position,
                        primary_color, '{}0'.format(nuclide))
    else:
        raise Exception("Invalid value")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create SVG format chart of nuclides')

    parser.add_argument('datafile', type=argparse.FileType('r'), 
                         help='Input data base XML file (required)')
    parser.add_argument('outfile', type=argparse.FileType('w'), 
                         help='Output data SVG file (required)')
    parser.add_argument('--names', action='store_false', 
                        help='Disable names')
    parser.add_argument('--halflives', action='store_false', 
                        help='Disable half-lives')
    parser.add_argument('--magic', action='store_false', 
                        help='Disable magic numbers')
    parser.add_argument('--numbers', action='store_false', 
                        help='Disable numbers along axis')
    parser.add_argument('--unknown', action='store_false', 
                        help='Disable isotopes with unknown decay mode')
    parser.add_argument('--z', nargs=2, default=[0,120],
                        dest='Z', type=int, help='Atomic number Z range (%(type)s), default: %(default)s')
    parser.add_argument('--n', nargs=2, default=[0,180],
                        dest='N', type=int, help='Neutron number N range (%(type)s), default: %(default)s')
    args = parser.parse_args()

    if args.N[0] > args.N[1]:
        print('Wrong N range {}, {}'.format(args.N[0], args.N[1]))
        print('Try {} -h for more information'.format(sys.argv[0]))
        exit()

    if args.Z[0] > args.Z[1]:
        print('Wrong Z range {}, {}'.format(args.Z[0], args.Z[1]))
        print('Try {} -h for more information'.format(sys.argv[0]))
        exit()


    # Create document type SVG and document itself with proper headers
    dom = xml.dom.minidom.getDOMImplementation()
    doctype_svg = dom.createDocumentType("svg", "-//W3C//DTD SVG 1.1//EN", "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd")
    svg = dom.createDocument("http://www.w3.org/2000/svg", "svg", doctype_svg)
    root = svg.documentElement
    root.setAttribute("xmlns", "http://www.w3.org/2000/svg")
    root.setAttribute("version", "1.1")
    
    # XML parser does not guarantee to preserve order of elements.
    # In fact minidom sorts elements alphabetically.
    # In SVG file order is important (elements added later appear at
    # the top of previous). To keep good order of elements we introduce
    # 4 layers (groups)
    #
    # layer0 is intended for squares (primary decay mode)
    # layer1 for triangles (secondary decay mode)
    # layer2 for magic number lines etc.
    # layer3 for text

    layers = []
    for l in range(5):
        layer = svg.createElement("g")
        layer.setAttribute("id", "layer{}".format(l))
        layer.setAttribute("fill", "none")
        root.appendChild(layer)
        layers.append(layer)

    n_limits = [None, None]
    z_limits = [None, None]
    data = load_xml_nuclear_table(args.datafile, args.N, args.Z,
                                  n_limits, z_limits)
   
    # Size of picture is now calculated, and proper attributes
    # are assigned to root element
    # Additional margins are added to provide space for numbers on the 
    # left and bottom
    size = [(n_limits[1] - n_limits[0] + 2) * SIZE_FIELD + SIZE_GAP,
            (z_limits[1] - z_limits[0] + 2) * SIZE_FIELD + SIZE_GAP]
    root.setAttribute("width", str(size[0]))
    root.setAttribute("height", str(size[1]))

    # This variable is used to draw numbers next to last 
    # first element in Z rows, and below first element in N column
    #
    # Could be used instead of n_magic and z_magic?
    shape = []
    for n in range(n_limits[0], n_limits[1] + 1):
        n_list = []
        for z in range(z_limits[0], z_limits[1] + 1):
            n_list.append(False)
        shape.append(n_list)

    n_magic = {}
    z_magic = {}
    for nuclide in data:
        N = nuclide.N
        Z = nuclide.Z
        if N in MAGIC_NUMBERS:
            if n_magic.get(N) is not None:
                if n_magic[N][1] < Z:
                    n_magic[N][1] = Z
            else:
                n_magic[N] = [Z, Z]
        if Z in MAGIC_NUMBERS:
            if z_magic.get(Z) is not None:
                if z_magic[Z][1] < N:
                    z_magic[Z][1] = N
            else:
                z_magic[Z] = [N, N]

        shape[N - n_limits[0]][Z - z_limits[0]] = True

        # Position is passed for upper left corner of square
        x = (N - n_limits[0] + 1) * SIZE_FIELD + SIZE_GAP
        y = size[1] - (Z - z_limits[0] + 2) * SIZE_FIELD 
        try:
            draw_nuclide(nuclide, layers, [x, y], args)
        except IndexError:
            print('IndexError: nuclide {}'.format(nuclide))
    if args.magic:
        draw_magic_lines(layers, n_magic, z_magic, n_limits, z_limits, size)
    if args.numbers:
        draw_numbers(layers, shape, n_limits, z_limits, size)


    # JEM: Draw Oslo upbend nuclei:
    for key, nuclide in oslo_nuclides.items():
        N = nuclide.N
        Z = nuclide.Z
        # if N in MAGIC_NUMBERS:
        #     if n_magic.get(N) is not None:
        #         if n_magic[N][1] < Z:
        #             n_magic[N][1] = Z
        #     else:
        #         n_magic[N] = [Z, Z]
        # if Z in MAGIC_NUMBERS:
        #     if z_magic.get(Z) is not None:
        #         if z_magic[Z][1] < N:
        #             z_magic[Z][1] = N
        #     else:
        #         z_magic[Z] = [N, N]

        # shape[N - n_limits[0]][Z - z_limits[0]] = True



        # Position is passed for upper left corner of square
        x = (N - n_limits[0] + 1) * SIZE_FIELD + SIZE_GAP
        y = size[1] - (Z - z_limits[0] + 2) * SIZE_FIELD 
        try:
            draw_Oslo_upbend_nuclei(nuclide, layers, [x, y], args)
        except IndexError:
            print('IndexError: nuclide {}'.format(nuclide))


        font_color = FONT_COLOR_DARK
        element_name = nuclide.element + " " + str(nuclide.A) 

        tx = x + SIZE_SHAPE / 2 
        ty = y + SIZE_GAP + 1.25 * SIZE_FONT

        # Add text to layer 4, which I added. Should be the very top layer. This is the only thing there.
        _draw_text(layers[4], [tx, ty], font_color, SIZE_FONT, element_name)



    args.outfile.write(svg.toprettyxml(indent="  ", encoding="utf-8").decode("utf-8"))
