"""
CLI tool for teachers to generate ILEARN practice worksheets.

Usage:
    py execution/generate_worksheet.py --standard 6.AF.3 --count 10
    py execution/generate_worksheet.py --standard 6.AF.3 --proficiency at --difficulty easy --count 5
    py execution/generate_worksheet.py --standard 6.AF.3 --stem 5 --count 20
    py execution/generate_worksheet.py --standard 6.AF.3 --count 10 --include-key --output my_worksheet.pdf
"""

import argparse
import os
import sys
import random

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from engine.models import ProficiencyLevel, Difficulty
from engine.stems.stem_6af1 import Stem6AF1
from engine.stems.stem_6af2 import Stem6AF2
from engine.stems.stem_6af3 import Stem6AF3
from engine.stems.stem_6af4 import Stem6AF4
from engine.stems.stem_7af1 import Stem7AF1
from engine.stems.stem_7af2 import Stem7AF2
from engine.stems.stem_7af3 import Stem7AF3
from engine.stems.stem_7af4 import Stem7AF4
from engine.stems.stem_7af5 import Stem7AF5
from engine.stems.stem_7af6 import Stem7AF6
from engine.stems.stem_8af1 import Stem8AF1
from engine.stems.stem_8af2 import Stem8AF2
from engine.stems.stem_8af3 import Stem8AF3
from engine.stems.stem_8af4 import Stem8AF4
from engine.stems.stem_8af5 import Stem8AF5
from engine.stems.stem_8af6 import Stem8AF6
from engine.stems.stem_8af7 import Stem8AF7
from engine.stems.stem_8af8 import Stem8AF8
from engine.stems.stem_6rp1 import Stem6RP1
from engine.stems.stem_6rp2 import Stem6RP2
from engine.stems.stem_6rp3 import Stem6RP3
from engine.stems.stem_6rp4 import Stem6RP4
from engine.stems.stem_6rp5 import Stem6RP5
from engine.stems.stem_6ns1 import Stem6NS1
from engine.stems.stem_6ns2 import Stem6NS2
from engine.stems.stem_6ns3 import Stem6NS3
from engine.stems.stem_6ns4 import Stem6NS4
from engine.stems.stem_6ns5 import Stem6NS5
from engine.stems.stem_6ns6 import Stem6NS6
from engine.stems.stem_6ns7 import Stem6NS7
from engine.stems.stem_6ns8 import Stem6NS8
from engine.stems.stem_6gm1 import Stem6GM1
from engine.stems.stem_6gm2 import Stem6GM2
from engine.stems.stem_6gm3 import Stem6GM3
from engine.stems.stem_6gm4 import Stem6GM4
from engine.stems.stem_7gm1 import Stem7GM1
from engine.stems.stem_7gm2 import Stem7GM2
from engine.stems.stem_7gm3 import Stem7GM3
from engine.stems.stem_8gm1 import Stem8GM1
from engine.stems.stem_8gm2 import Stem8GM2
from engine.stems.stem_8gm3 import Stem8GM3
from engine.stems.stem_7ns1 import Stem7NS1
from engine.stems.stem_7ns2 import Stem7NS2
from engine.stems.stem_7ns3 import Stem7NS3
from engine.stems.stem_7ns4 import Stem7NS4
from engine.stems.stem_7ns5 import Stem7NS5
from engine.stems.stem_7ns6 import Stem7NS6
from engine.stems.stem_7ns7 import Stem7NS7
from engine.stems.stem_7rp1 import Stem7RP1
from engine.stems.stem_7rp2 import Stem7RP2
from engine.stems.stem_7rp3 import Stem7RP3
from engine.stems.stem_8ns1 import Stem8NS1
from engine.stems.stem_8ns2 import Stem8NS2
from engine.stems.stem_8ns3 import Stem8NS3
from engine.stems.stem_8ns4 import Stem8NS4
from engine.stems.stem_6ds1 import Stem6DS1
from engine.stems.stem_6ds2 import Stem6DS2
from engine.stems.stem_6ds3 import Stem6DS3
from engine.stems.stem_6af5 import Stem6AF5
from engine.stems.stem_7dsp1 import Stem7DSP1
from engine.stems.stem_7dsp2 import Stem7DSP2
from engine.stems.stem_7dsp3 import Stem7DSP3
from engine.stems.stem_7dsp4 import Stem7DSP4
from engine.stems.stem_7dsp5 import Stem7DSP5
from engine.stems.stem_8dsp1 import Stem8DSP1
from engine.stems.stem_8dsp2 import Stem8DSP2
from engine.stems.stem_8dsp3 import Stem8DSP3
from engine.stems.stem_8dsp4 import Stem8DSP4
from engine.stems.stem_8dsp5 import Stem8DSP5
from engine.pdf_generator import generate_worksheet_pdf


# Registry of available stem generators
STEM_GENERATORS = {
    "6.AF.1": Stem6AF1,
    "6.AF.2": Stem6AF2,
    "6.AF.3": Stem6AF3,
    "6.AF.4": Stem6AF4,
    "7.AF.1": Stem7AF1,
    "7.AF.2": Stem7AF2,
    "7.AF.3": Stem7AF3,
    "7.AF.4": Stem7AF4,
    "7.AF.5": Stem7AF5,
    "7.AF.6": Stem7AF6,
    "8.AF.1": Stem8AF1,
    "8.AF.2": Stem8AF2,
    "8.AF.3": Stem8AF3,
    "8.AF.4": Stem8AF4,
    "8.AF.5": Stem8AF5,
    "8.AF.6": Stem8AF6,
    "8.AF.7": Stem8AF7,
    "8.AF.8": Stem8AF8,
    "6.RP.1": Stem6RP1,
    "6.RP.2": Stem6RP2,
    "6.RP.3": Stem6RP3,
    "6.RP.4": Stem6RP4,
    "6.RP.5": Stem6RP5,
    "6.NS.1": Stem6NS1,
    "6.NS.2": Stem6NS2,
    "6.NS.3": Stem6NS3,
    "6.NS.4": Stem6NS4,
    "6.NS.5": Stem6NS5,
    "6.NS.6": Stem6NS6,
    "6.NS.7": Stem6NS7,
    "6.NS.8": Stem6NS8,
    "6.GM.1": Stem6GM1,
    "6.GM.2": Stem6GM2,
    "6.GM.3": Stem6GM3,
    "6.GM.4": Stem6GM4,
    "7.GM.1": Stem7GM1,
    "7.GM.2": Stem7GM2,
    "7.GM.3": Stem7GM3,
    "8.GM.1": Stem8GM1,
    "8.GM.2": Stem8GM2,
    "8.GM.3": Stem8GM3,
    "7.NS.1": Stem7NS1,
    "7.NS.2": Stem7NS2,
    "7.NS.3": Stem7NS3,
    "7.NS.4": Stem7NS4,
    "7.NS.5": Stem7NS5,
    "7.NS.6": Stem7NS6,
    "7.NS.7": Stem7NS7,
    "7.RP.1": Stem7RP1,
    "7.RP.2": Stem7RP2,
    "7.RP.3": Stem7RP3,
    "8.NS.1": Stem8NS1,
    "8.NS.2": Stem8NS2,
    "8.NS.3": Stem8NS3,
    "8.NS.4": Stem8NS4,
    "6.DS.1": Stem6DS1,
    "6.DS.2": Stem6DS2,
    "6.DS.3": Stem6DS3,
    "6.AF.5": Stem6AF5,
    "7.DSP.1": Stem7DSP1,
    "7.DSP.2": Stem7DSP2,
    "7.DSP.3": Stem7DSP3,
    "7.DSP.4": Stem7DSP4,
    "7.DSP.5": Stem7DSP5,
    "8.DSP.1": Stem8DSP1,
    "8.DSP.2": Stem8DSP2,
    "8.DSP.3": Stem8DSP3,
    "8.DSP.4": Stem8DSP4,
    "8.DSP.5": Stem8DSP5,
}

STANDARD_INFO = {
    "6.AF.1": {
        "text": "Define and use multiple variables when writing expressions to represent real-world and other mathematical problems, and evaluate them for given values.",
        "category": "Algebra and Functions",
        "subdomain": "Expressions and Data Analysis",
        "calculator": "Not Allowed",
    },
    "6.AF.2": {
        "text": "Demonstrate which values from a specified set, if any, make the equation or inequality true. Use substitution to determine whether a given number in a specified set makes an equation or inequality true.",
        "category": "Algebra and Functions",
        "subdomain": "Equations and Inequalities",
        "calculator": "Not Allowed",
    },
    "6.AF.3": {
        "text": "Solve equations of the form x + p = q, x - p = q, px = q, and x/p = q fluently for cases in which p, q and x are all nonnegative rational numbers.",
        "category": "Algebra and Functions",
        "subdomain": "Equations and Inequalities",
        "calculator": "Not Allowed",
    },
    "6.AF.4": {
        "text": "Write an inequality of the form x > c, x >= c, x < c, or x <= c to represent a constraint or condition in a real-world or other mathematical problem.",
        "category": "Algebra and Functions",
        "subdomain": "Equations and Inequalities",
        "calculator": "Not Allowed",
    },
    "7.AF.1": {
        "text": "Apply the properties of operations to generate equivalent linear expressions, including adding, subtracting, factoring, and expanding, to prepare for solving linear equations.",
        "category": "Algebra and Functions",
        "subdomain": "Expressions",
        "calculator": "Not Allowed",
    },
    "7.AF.2": {
        "text": "Solve real-world problems with rational numbers by using one or two operations.",
        "category": "Algebra and Functions",
        "subdomain": "Expressions",
        "calculator": "Not Allowed",
    },
    "7.AF.3": {
        "text": "Solve equations of the form px + q = r and p(x + q) = r fluently, where p, q, and r are specific rational numbers.",
        "category": "Algebra and Functions",
        "subdomain": "Equations and Inequalities",
        "calculator": "Allowed",
    },
    "7.AF.4": {
        "text": "Solve inequalities of the form px + q (> or <) r and p(x + q) (> or <) r, where p, q, and r are specific rational numbers.",
        "category": "Algebra and Functions",
        "subdomain": "Equations and Inequalities",
        "calculator": "Allowed",
    },
    "7.AF.5": {
        "text": "Identify, describe, and analyze linear relationships between two variables.",
        "category": "Algebra and Functions",
        "subdomain": "Linear Relationships",
        "calculator": "Allowed",
    },
    "7.AF.6": {
        "text": "Graph a line given its slope and a point on the line. Find the slope of a line given its graph.",
        "category": "Algebra and Functions",
        "subdomain": "Linear Relationships",
        "calculator": "Allowed",
    },
    "8.AF.1": {
        "text": "Solve linear equations and inequalities with rational number coefficients fluently.",
        "category": "Algebra and Functions",
        "subdomain": "Equations and Inequalities",
        "calculator": "Allowed",
    },
    "8.AF.2": {
        "text": "Generate linear equations with one solution, infinitely many solutions, or no solutions.",
        "category": "Algebra and Functions",
        "subdomain": "Equations and Inequalities",
        "calculator": "Allowed",
    },
    "8.AF.3": {
        "text": "Understand that a function assigns to each x-value exactly one y-value.",
        "category": "Algebra and Functions",
        "subdomain": "Functions",
        "calculator": "Allowed",
    },
    "8.AF.4": {
        "text": "Describe qualitatively the functional relationship between two quantities by analyzing a graph.",
        "category": "Algebra and Functions",
        "subdomain": "Functions",
        "calculator": "Allowed",
    },
    "8.AF.5": {
        "text": "Interpret y = mx + b as defining a linear function. Describe linear vs nonlinear functions.",
        "category": "Algebra and Functions",
        "subdomain": "Linear Functions",
        "calculator": "Allowed",
    },
    "8.AF.6": {
        "text": "Construct a function to model a linear relationship. Describe the meaning of m and b.",
        "category": "Algebra and Functions",
        "subdomain": "Linear Functions",
        "calculator": "Allowed",
    },
    "8.AF.7": {
        "text": "Compare properties of two linear functions given in different forms.",
        "category": "Algebra and Functions",
        "subdomain": "Linear Functions",
        "calculator": "Allowed",
    },
    "8.AF.8": {
        "text": "Approximate the solution of a system of equations by graphing.",
        "category": "Algebra and Functions",
        "subdomain": "Linear Functions",
        "calculator": "Allowed",
    },
    "6.RP.1": {
        "text": "Convert between any two representations (fractions, decimals, percents) of positive rational numbers without the use of a calculator.",
        "category": "Ratios and Proportional Reasoning",
        "subdomain": "Operations with Positive Numbers",
        "calculator": "Not Allowed",
    },
    "6.RP.2": {
        "text": "Understand the concept of a unit rate and use terms related to rate in the context of a ratio relationship.",
        "category": "Ratios and Proportional Reasoning",
        "subdomain": "Working with Rates and Ratios",
        "calculator": "Allowed",
    },
    "6.RP.3": {
        "text": "Make tables of equivalent ratios relating quantities with whole-number measurements, find missing values in the tables, and plot the pairs of values on the coordinate plane.",
        "category": "Ratios and Proportional Reasoning",
        "subdomain": "Working with Rates and Ratios",
        "calculator": "Allowed",
    },
    "6.RP.4": {
        "text": "Solve real-world and other mathematical problems involving rates and ratios using models and strategies.",
        "category": "Ratios and Proportional Reasoning",
        "subdomain": "Solving Problems with Rates, Ratios, and Proportions",
        "calculator": "Allowed",
    },
    "6.RP.5": {
        "text": "Use variables to represent two quantities in a proportional relationship; write an equation y = px and analyze using graphs and tables.",
        "category": "Ratios and Proportional Reasoning",
        "subdomain": "Solving Problems with Rates, Ratios, and Proportions",
        "calculator": "Allowed",
    },
    "6.NS.1": {
        "text": "Understand that positive and negative numbers are used to describe quantities having opposite directions or values. Use positive and negative numbers to represent and compare quantities in real-world contexts.",
        "category": "Number Sense",
        "subdomain": "Integers",
        "calculator": "Not Allowed",
    },
    "6.NS.2": {
        "text": "Understand opposite numbers on the number line. Use positive and negative numbers to represent quantities in real-world contexts.",
        "category": "Number Sense",
        "subdomain": "Integers",
        "calculator": "Not Allowed",
    },
    "6.NS.3": {
        "text": "Compare and order rational numbers and plot them on a number line. Write, interpret, and explain statements of order for rational numbers in real-world contexts.",
        "category": "Number Sense",
        "subdomain": "Integers",
        "calculator": "Not Allowed",
    },
    "6.NS.4": {
        "text": "Solve real-world problems with positive fractions and decimals by using one or two operations.",
        "category": "Number Sense",
        "subdomain": "Operations with Positive Numbers",
        "calculator": "Not Allowed",
    },
    "6.NS.5": {
        "text": "Know and use the order of operations to evaluate written numerical expressions involving non-negative rational numbers.",
        "category": "Number Sense",
        "subdomain": "Order of Operations",
        "calculator": "Not Allowed",
    },
    "6.NS.6": {
        "text": "Find the greatest common factor (GCF) of two whole numbers less than or equal to 100 and the least common multiple (LCM) of two whole numbers less than or equal to 12. Use the distributive property to express a sum of two whole numbers with a common factor.",
        "category": "Number Sense",
        "subdomain": "Factors and Multiples",
        "calculator": "Not Allowed",
    },
    "6.NS.7": {
        "text": "Apply the properties of operations to generate equivalent expressions.",
        "category": "Number Sense",
        "subdomain": "Expressions",
        "calculator": "Not Allowed",
    },
    "6.NS.8": {
        "text": "Evaluate and write numerical expressions involving positive rational bases and whole number exponents.",
        "category": "Number Sense",
        "subdomain": "Exponents",
        "calculator": "Not Allowed",
    },
    "6.GM.1": {
        "text": "Convert between measurement systems (customary to metric and metric to customary) given the conversion factors.",
        "category": "Geometry and Measurement",
        "subdomain": "Unit Conversion",
        "calculator": "Allowed",
    },
    "6.GM.2": {
        "text": "Apply the sums of interior angles of triangles and quadrilaterals to solve real-world and mathematical problems.",
        "category": "Geometry and Measurement",
        "subdomain": "Angle Sums",
        "calculator": "Allowed",
    },
    "6.GM.3": {
        "text": "Find the area of complex shapes composed of polygons by composing or decomposing into simple shapes.",
        "category": "Geometry and Measurement",
        "subdomain": "Composite Area",
        "calculator": "Allowed",
    },
    "6.GM.4": {
        "text": "Find the volume of a right rectangular prism with fractional edge lengths using unit cubes.",
        "category": "Geometry and Measurement",
        "subdomain": "Volume",
        "calculator": "Allowed",
    },
    "7.GM.1": {
        "text": "Solve problems involving scale drawings of geometric figures.",
        "category": "Geometry and Measurement",
        "subdomain": "Scale Drawings",
        "calculator": "Allowed",
    },
    "7.GM.2": {
        "text": "Identify and use the formulas for the area and circumference of a circle to solve problems.",
        "category": "Geometry and Measurement",
        "subdomain": "Circle Area and Circumference",
        "calculator": "Allowed",
    },
    "7.GM.3": {
        "text": "Know and use the formulas for the volume of cylinders and composite right rectangular prisms.",
        "category": "Geometry and Measurement",
        "subdomain": "Volume of Cylinders and Composite Prisms",
        "calculator": "Allowed",
    },
    "8.GM.1": {
        "text": "Identify, describe, and perform transformations on figures in a coordinate plane.",
        "category": "Geometry and Measurement",
        "subdomain": "Transformations",
        "calculator": "Allowed",
    },
    "8.GM.2": {
        "text": "Know and use the formulas for the volumes of cones, spheres, and pyramids and the surface area of spheres.",
        "category": "Geometry and Measurement",
        "subdomain": "Volume and Surface Area",
        "calculator": "Allowed",
    },
    "8.GM.3": {
        "text": "Apply the Pythagorean Theorem to determine unknown side lengths in right triangles.",
        "category": "Geometry and Measurement",
        "subdomain": "Pythagorean Theorem",
        "calculator": "Allowed",
    },
    "7.NS.1": {
        "text": "Find the sum of rational numbers and represent real-world contexts using sums. Understand p + q as the number located a distance |q| from p.",
        "category": "Number Sense",
        "subdomain": "Operations with Signed Numbers",
        "calculator": "Not Allowed",
    },
    "7.NS.2": {
        "text": "Find the difference of rational numbers, including representing addition and subtraction on a number line diagram.",
        "category": "Number Sense",
        "subdomain": "Operations with Signed Numbers",
        "calculator": "Not Allowed",
    },
    "7.NS.3": {
        "text": "Find the product of rational numbers and describe real-world contexts. Understand rules for multiplying signed numbers.",
        "category": "Number Sense",
        "subdomain": "Operations with Signed Numbers",
        "calculator": "Not Allowed",
    },
    "7.NS.4": {
        "text": "Find the quotient of rational numbers and describe real-world contexts. Understand that -(p/q) = (-p)/q = p/(-q).",
        "category": "Number Sense",
        "subdomain": "Operations with Signed Numbers",
        "calculator": "Not Allowed",
    },
    "7.NS.5": {
        "text": "Find prime factorizations of whole numbers and write them using exponents.",
        "category": "Number Sense",
        "subdomain": "Prime Factorization",
        "calculator": "Not Allowed",
    },
    "7.NS.6": {
        "text": "Evaluate the square roots of perfect squares less than or equal to 625. Understand that positive square roots of non-perfect-squares are irrational.",
        "category": "Number Sense",
        "subdomain": "Square Roots",
        "calculator": "Not Allowed",
    },
    "7.NS.7": {
        "text": "Compute fluently with rational numbers (positive and negative fractions, decimals, and integers) using the order of operations.",
        "category": "Number Sense",
        "subdomain": "Operations with Signed Numbers",
        "calculator": "Not Allowed",
    },
    "7.RP.1": {
        "text": "Compute unit rates associated with ratios of fractions. Identify the constant of proportionality in tables, graphs, equations, and verbal descriptions.",
        "category": "Ratios and Proportional Reasoning",
        "subdomain": "Proportional Relationships",
        "calculator": "Allowed",
    },
    "7.RP.2": {
        "text": "Solve real-world problems involving percent including discounts and markups, simple interest, tax, tips, and percent of change.",
        "category": "Ratios and Proportional Reasoning",
        "subdomain": "Percent Problems",
        "calculator": "Allowed",
    },
    "7.RP.3": {
        "text": "Recognize and represent proportional relationships between quantities. Write y = mx equations from tables and verbal descriptions.",
        "category": "Ratios and Proportional Reasoning",
        "subdomain": "Proportional Relationships",
        "calculator": "Allowed",
    },
    "8.NS.1": {
        "text": "Give examples of rational and irrational numbers and explain the difference. Understand that every number has a decimal expansion.",
        "category": "Number Sense",
        "subdomain": "Rational and Irrational Numbers",
        "calculator": "Not Allowed",
    },
    "8.NS.2": {
        "text": "Use rational approximations of irrational numbers to compare sizes, locate on number lines, and estimate expressions.",
        "category": "Number Sense",
        "subdomain": "Rational and Irrational Numbers",
        "calculator": "Not Allowed",
    },
    "8.NS.3": {
        "text": "Know and apply the properties of integer exponents to generate equivalent numerical expressions.",
        "category": "Number Sense",
        "subdomain": "Exponents",
        "calculator": "Not Allowed",
    },
    "8.NS.4": {
        "text": "Solve real-world problems with rational numbers by using multiple operations.",
        "category": "Number Sense",
        "subdomain": "Operations with Rationals",
        "calculator": "Allowed",
    },
    "6.DS.1": {
        "text": "Recognize and represent data with appropriate graphical displays including dot plots, histograms, and box plots.",
        "category": "Data Analysis & Statistics",
        "subdomain": "Graphical Representations",
        "calculator": "Allowed",
    },
    "6.DS.2": {
        "text": "Formulate statistical questions; collect and organize data from relevant responses.",
        "category": "Data Analysis & Statistics",
        "subdomain": "Statistical Questions",
        "calculator": "Allowed",
    },
    "6.DS.3": {
        "text": "Determine quantitative measures of center and variability; describe overall patterns and outliers.",
        "category": "Data Analysis & Statistics",
        "subdomain": "Summarizing Data",
        "calculator": "Allowed",
    },
    "6.AF.5": {
        "text": "Plot points in all four quadrants of the coordinate plane; find distances between points with same first or second coordinate.",
        "category": "Algebra and Functions",
        "subdomain": "Coordinate Plane",
        "calculator": "Not Allowed",
    },
    "7.DSP.1": {
        "text": "Understand that statistics can be used to gain information about a population by examining a representative sample.",
        "category": "Data Analysis, Statistics & Probability",
        "subdomain": "Sampling & Populations",
        "calculator": "Allowed",
    },
    "7.DSP.2": {
        "text": "Use measures of center and variability from random samples to draw informal comparative inferences about two populations.",
        "category": "Data Analysis, Statistics & Probability",
        "subdomain": "Comparing Populations",
        "calculator": "Allowed",
    },
    "7.DSP.3": {
        "text": "Visually assess the degree of overlap between two numerical data distributions with similar variabilities.",
        "category": "Data Analysis, Statistics & Probability",
        "subdomain": "Visual Overlap",
        "calculator": "Allowed",
    },
    "7.DSP.4": {
        "text": "Understand that the probability of a chance event is a number between 0 and 1. Classify events by likelihood.",
        "category": "Data Analysis, Statistics & Probability",
        "subdomain": "Probability Fundamentals",
        "calculator": "Allowed",
    },
    "7.DSP.5": {
        "text": "Develop probability models. Predict approximate relative frequency. Compare model probabilities to observed frequencies.",
        "category": "Data Analysis, Statistics & Probability",
        "subdomain": "Probability Models",
        "calculator": "Allowed",
    },
    "8.DSP.1": {
        "text": "Construct and describe scatter plots for bivariate measurement data; identify associations and features.",
        "category": "Data Analysis, Statistics & Probability",
        "subdomain": "Scatter Plots",
        "calculator": "Allowed",
    },
    "8.DSP.2": {
        "text": "Know that lines are widely used to model relationships between two quantitative variables. Use slope-intercept form.",
        "category": "Data Analysis, Statistics & Probability",
        "subdomain": "Linear Models",
        "calculator": "Allowed",
    },
    "8.DSP.3": {
        "text": "Represent sample spaces and find probabilities of compound events using organized lists, tables, and tree diagrams.",
        "category": "Data Analysis, Statistics & Probability",
        "subdomain": "Compound Events",
        "calculator": "Allowed",
    },
    "8.DSP.4": {
        "text": "Define the probability of a compound event as the fraction of outcomes. Use terminology for event types.",
        "category": "Data Analysis, Statistics & Probability",
        "subdomain": "Event Classification",
        "calculator": "Allowed",
    },
    "8.DSP.5": {
        "text": "Represent the sample space of compound events using the Multiplication Counting Principle.",
        "category": "Data Analysis, Statistics & Probability",
        "subdomain": "Counting Principle",
        "calculator": "Allowed",
    },
}

PROFICIENCY_MAP = {
    "below": ProficiencyLevel.BELOW,
    "approaching": ProficiencyLevel.APPROACHING,
    "at": ProficiencyLevel.AT,
    "above": ProficiencyLevel.ABOVE,
}

DIFFICULTY_MAP = {
    "easy": Difficulty.EASY,
    "medium": Difficulty.MEDIUM,
    "difficult": Difficulty.DIFFICULT,
}


def main():
    parser = argparse.ArgumentParser(
        description="Generate ILEARN math practice worksheets",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Generate 10 mixed questions:
    py execution/generate_worksheet.py --standard 6.AF.3 --count 10

  Generate 5 At-Proficiency Easy questions:
    py execution/generate_worksheet.py --standard 6.AF.3 --proficiency at --difficulty easy --count 5

  Generate 20 variants of stem 5 (height comparison):
    py execution/generate_worksheet.py --standard 6.AF.3 --stem 5 --count 20

  Generate with answer key:
    py execution/generate_worksheet.py --standard 6.AF.3 --count 10 --include-key
        """
    )
    parser.add_argument("--standard", required=True,
                        choices=list(STEM_GENERATORS.keys()),
                        help="Standard code (e.g., 6.AF.3)")
    parser.add_argument("--proficiency",
                        choices=["below", "approaching", "at", "above", "mixed"],
                        default="mixed",
                        help="Proficiency level filter (default: mixed)")
    parser.add_argument("--difficulty",
                        choices=["easy", "medium", "difficult", "mixed"],
                        default="mixed",
                        help="Difficulty filter (default: mixed)")
    parser.add_argument("--stem", type=int, default=None,
                        help="Generate variants of a specific stem (1-7 for 6.AF.3)")
    parser.add_argument("--count", type=int, default=10,
                        help="Number of questions to include (default: 10)")
    parser.add_argument("--seed", type=int, default=42,
                        help="Random seed for reproducible worksheets (default: 42)")
    parser.add_argument("--include-key", action="store_true",
                        help="Include a separate answer key PDF")
    parser.add_argument("--output", default=None,
                        help="Output PDF path (default: .tmp/{standard}_worksheet.pdf)")
    parser.add_argument("--list-stems", action="store_true",
                        help="List available stems for the standard and exit")

    args = parser.parse_args()

    # Get generator class
    gen_class = STEM_GENERATORS[args.standard]
    info = STANDARD_INFO[args.standard]

    if args.list_stems:
        print(f"\nStems for {args.standard}:")
        print(f"{'='*60}")
        gen = gen_class(seed=args.seed)
        # Generate one of each to show what they look like
        for stem_idx in range(1, 20):
            try:
                qs = gen.generate_stem_variants(stem_idx, variants_per_stem=1)
            except ValueError:
                break
            if qs:
                q = qs[0]
                print(f"\n  Stem {stem_idx}: {q.proficiency_level.value} | {q.difficulty.value} | {q.item_type.value} | DOK {q.dok}")
                preview = q.stem_text[:100].replace('\n', ' ')
                print(f"  Preview: {preview}...")
        return

    # Generate all variants
    gen = gen_class(seed=args.seed)

    if args.stem:
        all_questions = gen.generate_stem_variants(args.stem, variants_per_stem=max(args.count, 20))
    else:
        all_questions = gen.generate_all_variants(variants_per_stem=20)

    # Filter by proficiency
    if args.proficiency != "mixed":
        target_prof = PROFICIENCY_MAP[args.proficiency]
        all_questions = [q for q in all_questions if q.proficiency_level == target_prof]

    # Filter by difficulty
    if args.difficulty != "mixed":
        target_diff = DIFFICULTY_MAP[args.difficulty]
        all_questions = [q for q in all_questions if q.difficulty == target_diff]

    if not all_questions:
        print(f"No questions match the filters. Try broader criteria.")
        return

    # Select the requested count
    rng = random.Random(args.seed)
    if len(all_questions) > args.count:
        selected = rng.sample(all_questions, args.count)
    else:
        selected = all_questions[:args.count]

    # Sort by stem index for a logical flow
    selected.sort(key=lambda q: (q.stem_index, q.variant_index))

    # Output path
    if args.output:
        output_path = args.output
    else:
        os.makedirs(".tmp", exist_ok=True)
        safe_code = args.standard.replace(".", "")
        output_path = os.path.join(".tmp", f"{safe_code}_worksheet.pdf")

    # Generate PDF
    print(f"\nGenerating {len(selected)} questions for {args.standard}...")
    print(f"Proficiency: {args.proficiency} | Difficulty: {args.difficulty}")
    if args.stem:
        print(f"Stem: {args.stem}")
    print()

    generate_worksheet_pdf(
        questions=selected,
        output_path=output_path,
        title="ILEARN Practice",
        standard_code=args.standard,
        standard_text=info["text"],
        category=info["category"],
        subdomain=info["subdomain"],
        calculator=info["calculator"],
        include_answer_key=args.include_key,
    )

    print(f"\nDone! {len(selected)} questions written to {output_path}")
    if args.include_key:
        key_path = output_path.replace(".pdf", "_answer_key.pdf")
        print(f"Answer key: {key_path}")


if __name__ == "__main__":
    main()
