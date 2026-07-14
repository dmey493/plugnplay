"""
Context pools for generating diverse, culturally appropriate word problems.
Each pool provides templates for specific equation forms and real-world scenarios.
"""


# Diverse name pools - culturally representative
NAMES = {
    "male": [
        "Marcus", "Jayden", "Carlos", "Wei", "Amir", "Ethan", "DeShaun",
        "Leo", "Raj", "Tyler", "Noah", "Diego", "Kenji", "Omar", "Isaiah",
        "Mateo", "Kai", "Andre", "Liam", "Ravi"
    ],
    "female": [
        "Aaliyah", "Sofia", "Maya", "Lin", "Priya", "Emma", "Destiny",
        "Yuki", "Rosa", "Grace", "Zara", "Amara", "Mei", "Fatima", "Lily",
        "Carmen", "Nia", "Sakura", "Elena", "Jasmine"
    ],
    "neutral": [
        "Alex", "Jordan", "Sam", "Riley", "Taylor", "Quinn", "Morgan",
        "Sage", "Rowan", "Kai", "Jamie", "Avery", "Harper", "Skyler"
    ]
}

# Relationship pairs for comparison problems
RELATIONSHIPS = [
    ("brother", "sister"), ("sister", "brother"),
    ("student", "teacher"), ("friend", "friend"),
    ("parent", "child"), ("teammate", "teammate"),
]

# Units for various measurement contexts
UNITS = {
    "length": ["inches", "feet", "centimeters", "meters", "yards"],
    "weight": ["pounds", "ounces", "kilograms", "grams"],
    "volume": ["cups", "pints", "quarts", "gallons", "liters", "milliliters"],
    "money": ["dollars"],
    "pages": ["pages"],
    "items": ["marbles", "stickers", "cards", "tokens", "points", "stamps"],
    "food": ["cups of food", "slices", "pieces", "servings", "pints"],
    "time": ["minutes", "hours"],
    "distance": ["miles", "kilometers", "blocks"],
}


# ============================================================
# CONTEXTS FOR 6.AF.3 EQUATION FORMS
# ============================================================
# Each context dict has:
#   template: str with {name}, {p}, {q}, {x}, {var} placeholders
#   variable_desc: what the variable represents
#   unit: measurement unit
#   var_letter: suggested variable letter
#   scenario_type: category for the answer key

CONTEXTS_6AF3_ADD = [
    # x + p = q  (student finds x)
    {
        "template": "{name} read some pages of a book on Monday. On Tuesday, {name} read {p} more pages. In total, {name} read {q} pages.",
        "variable_desc": "the number of pages {name} read on Monday",
        "unit": "pages",
        "var_letter": "x",
        "scenario_type": "reading"
    },
    {
        "template": "{name} has some stickers. After receiving {p} more stickers from a friend, {name} now has {q} stickers total.",
        "variable_desc": "the number of stickers {name} started with",
        "unit": "stickers",
        "var_letter": "s",
        "scenario_type": "collecting"
    },
    {
        "template": "{name} is saving money. After earning ${p} from doing chores, {name} now has ${q} in savings.",
        "variable_desc": "the amount of money {name} had before doing chores",
        "unit": "dollars",
        "var_letter": "m",
        "scenario_type": "money"
    },
    {
        "template": "{name} walked some distance in the morning. In the afternoon, {name} walked {p} miles. {name} walked {q} miles in total that day.",
        "variable_desc": "the distance {name} walked in the morning",
        "unit": "miles",
        "var_letter": "d",
        "scenario_type": "distance"
    },
    {
        "template": "{name} spent some time studying math. Then {name} spent {p} minutes studying science. {name} studied for {q} minutes total.",
        "variable_desc": "the time {name} spent studying math",
        "unit": "minutes",
        "var_letter": "t",
        "scenario_type": "time"
    },
    {
        "template": "{name} scored some points in the first half of a game. In the second half, {name} scored {p} points. {name} scored {q} points total.",
        "variable_desc": "the number of points {name} scored in the first half",
        "unit": "points",
        "var_letter": "p",
        "scenario_type": "sports"
    },
    {
        "template": "{name} has two containers of juice. One container holds some juice and the other holds {p} ounces. Together, the containers hold {q} ounces.",
        "variable_desc": "the amount of juice in the first container",
        "unit": "ounces",
        "var_letter": "j",
        "scenario_type": "volume"
    },
    {
        "template": "{name} collected some canned goods for a food drive on the first day. On the second day, {name} collected {p} more cans. {name} collected {q} cans in all.",
        "variable_desc": "the number of cans {name} collected on the first day",
        "unit": "cans",
        "var_letter": "c",
        "scenario_type": "community"
    },
]

CONTEXTS_6AF3_SUBTRACT = [
    # x - p = q  (student finds x)
    {
        "template": "{name} had some trading cards. After giving away {p} cards to a friend, {name} has {q} cards left.",
        "variable_desc": "the number of cards {name} started with",
        "unit": "cards",
        "var_letter": "c",
        "scenario_type": "collecting"
    },
    {
        "template": "{name} had some money. After spending ${p} on lunch, {name} has ${q} left.",
        "variable_desc": "the amount of money {name} started with",
        "unit": "dollars",
        "var_letter": "m",
        "scenario_type": "money"
    },
    {
        "template": "A container had some water in it. After {p} liters were poured out, there were {q} liters remaining.",
        "variable_desc": "the original amount of water in the container",
        "unit": "liters",
        "var_letter": "w",
        "scenario_type": "volume"
    },
    {
        "template": "{name} had some marbles. After losing {p} marbles during a game, {name} has {q} marbles left.",
        "variable_desc": "the number of marbles {name} had before the game",
        "unit": "marbles",
        "var_letter": "m",
        "scenario_type": "game"
    },
    {
        "template": "A store had some apples. After selling {p} apples, the store has {q} apples left.",
        "variable_desc": "the number of apples the store started with",
        "unit": "apples",
        "var_letter": "a",
        "scenario_type": "store"
    },
    {
        "template": "{name} drove some distance. After driving past a rest stop that was {p} miles from the start, {name} still had {q} miles left to drive.",
        "variable_desc": "the total distance of {name}'s trip",
        "unit": "miles",
        "var_letter": "d",
        "scenario_type": "distance"
    },
    {
        "template": "{name} baked some cookies. After giving {p} cookies to a neighbor, {name} has {q} cookies remaining.",
        "variable_desc": "the number of cookies {name} baked",
        "unit": "cookies",
        "var_letter": "c",
        "scenario_type": "baking"
    },
    {
        "template": "A library had some books on a shelf. After {p} books were checked out, {q} books remained on the shelf.",
        "variable_desc": "the number of books originally on the shelf",
        "unit": "books",
        "var_letter": "b",
        "scenario_type": "library"
    },
]

CONTEXTS_6AF3_MULTIPLY = [
    # px = q  (student finds x)
    {
        "template": "A {relation1} is {p} times as tall as their {relation2}. The {relation1} is {q} inches tall. The {relation2} is {var} inches tall.",
        "variable_desc": "the height of the {relation2}",
        "unit": "inches",
        "var_letter": "x",
        "scenario_type": "measurement",
        "uses_relationship": True
    },
    {
        "template": "{name} earns ${p} per hour. {name} earned ${q} in total. Let {var} represent the number of hours worked.",
        "variable_desc": "the number of hours {name} worked",
        "unit": "hours",
        "var_letter": "h",
        "scenario_type": "money"
    },
    {
        "template": "Each box contains {p} items. There are {q} items in total. Let {var} represent the number of boxes.",
        "variable_desc": "the number of boxes",
        "unit": "boxes",
        "var_letter": "b",
        "scenario_type": "packing"
    },
    {
        "template": "{name} runs {p} miles each day. After some number of days, {name} has run {q} miles total. Let {var} represent the number of days.",
        "variable_desc": "the number of days {name} ran",
        "unit": "days",
        "var_letter": "d",
        "scenario_type": "exercise"
    },
    {
        "template": "A recipe calls for {p} cups of flour per batch. {name} needs {q} cups of flour total. Let {var} represent the number of batches.",
        "variable_desc": "the number of batches {name} is making",
        "unit": "batches",
        "var_letter": "n",
        "scenario_type": "cooking"
    },
    {
        "template": "{name}'s garden has {p} rows of plants. There are {q} plants in total. Let {var} represent the number of plants per row.",
        "variable_desc": "the number of plants in each row",
        "unit": "plants per row",
        "var_letter": "r",
        "scenario_type": "garden"
    },
    {
        "template": "Each ticket costs ${p}. The total cost for all tickets is ${q}. Let {var} represent the number of tickets purchased.",
        "variable_desc": "the number of tickets purchased",
        "unit": "tickets",
        "var_letter": "t",
        "scenario_type": "purchasing"
    },
    {
        "template": "A car travels {p} miles per gallon of gas. The car traveled {q} miles. Let {var} represent the number of gallons of gas used.",
        "variable_desc": "the gallons of gas used",
        "unit": "gallons",
        "var_letter": "g",
        "scenario_type": "travel"
    },
]

CONTEXTS_6AF3_DIVIDE = [
    # x/p = q  (student finds x)
    {
        "template": "A group of {p} friends share some {item} equally. Each friend receives {q} {item}.",
        "variable_desc": "the total number of {item}",
        "unit": "{item}",
        "var_letter": "x",
        "scenario_type": "sharing",
        "item_options": ["pints of ice cream", "slices of pizza", "granola bars", "juice boxes", "stickers"]
    },
    {
        "template": "{name} divides a collection of stamps into {p} equal groups. Each group has {q} stamps.",
        "variable_desc": "the total number of stamps",
        "unit": "stamps",
        "var_letter": "s",
        "scenario_type": "organizing"
    },
    {
        "template": "{name} cuts a ribbon into {p} equal pieces. Each piece is {q} inches long.",
        "variable_desc": "the total length of the ribbon",
        "unit": "inches",
        "var_letter": "r",
        "scenario_type": "measurement"
    },
    {
        "template": "A teacher divides {var} pencils equally among {p} students. Each student gets {q} pencils.",
        "variable_desc": "the total number of pencils",
        "unit": "pencils",
        "var_letter": "n",
        "scenario_type": "classroom"
    },
    {
        "template": "{name} has some money to split equally among {p} jars for saving. Each jar gets ${q}.",
        "variable_desc": "the total amount of money",
        "unit": "dollars",
        "var_letter": "m",
        "scenario_type": "money"
    },
    {
        "template": "A farmer divides a field into {p} equal sections. Each section is {q} acres.",
        "variable_desc": "the total area of the field",
        "unit": "acres",
        "var_letter": "a",
        "scenario_type": "farming"
    },
    {
        "template": "{name} pours water equally into {p} containers. Each container gets {q} cups of water.",
        "variable_desc": "the total amount of water",
        "unit": "cups",
        "var_letter": "w",
        "scenario_type": "volume"
    },
    {
        "template": "A race course is divided into {p} equal legs. Each leg is {q} miles long.",
        "variable_desc": "the total length of the race course",
        "unit": "miles",
        "var_letter": "d",
        "scenario_type": "sports"
    },
]

# Contexts for "Above Proficiency" budget/rounding problems (px = q where answer requires interpretation)
CONTEXTS_6AF3_ABOVE = [
    {
        "template": "{name} wants to buy {item} for a class party.\n- Each {item_singular} costs ${p}.\n- {name} has a maximum of ${q} to spend.\n\nIn the box below, write an equation to represent how many {item} {name} can buy. Show the steps to solving the equation and explain how many whole {item} {name} can buy.",
        "variable_desc": "the number of {item} {name} can buy",
        "unit": "{item}",
        "var_letter": "x",
        "scenario_type": "budgeting",
        "items": [
            ("pizzas", "pizza"), ("notebooks", "notebook"), ("packs of markers", "pack of markers"),
            ("bags of chips", "bag of chips"), ("bottles of water", "bottle of water"),
            ("boxes of crayons", "box of crayons"), ("science kits", "science kit"),
            ("packs of pencils", "pack of pencils"),
        ]
    },
    {
        "template": "{name} is making gift bags for a school event.\n- Each gift bag needs {p} feet of ribbon.\n- {name} has {q} feet of ribbon.\n\nWrite an equation, solve it, and explain how many complete gift bags {name} can make.",
        "variable_desc": "the number of gift bags {name} can make",
        "unit": "gift bags",
        "var_letter": "g",
        "scenario_type": "crafting"
    },
    {
        "template": "A bus can hold {p} passengers. There are {q} people waiting to go on a field trip.\n\nWrite an equation to find the number of buses needed. Show your work and explain how many buses are actually needed.",
        "variable_desc": "the number of buses needed",
        "unit": "buses",
        "var_letter": "b",
        "scenario_type": "transportation"
    },
]


def pick_name(rng, gender=None):
    """Pick a random name from the pool."""
    if gender is None:
        gender = rng.choice(["male", "female", "neutral"])
    return rng.choice(NAMES[gender])


def pick_name_pair(rng):
    """Pick two different names."""
    name1 = pick_name(rng)
    name2 = pick_name(rng)
    while name2 == name1:
        name2 = pick_name(rng)
    return name1, name2


def pick_relationship(rng):
    """Pick a relationship pair."""
    return rng.choice(RELATIONSHIPS)


# ============================================================
# CONTEXTS FOR 7.AF.2 — REAL-WORLD RATIONAL NUMBER PROBLEMS
# ============================================================

CONTEXTS_7AF2_PRICE_CHANGE = [
    {
        "item": "a gallon of gasoline",
        "base_price": 3.50,
        "changes": ["increased by", "decreased by", "increased by", "decreased by"],
    },
    {
        "item": "a dozen eggs",
        "base_price": 2.80,
        "changes": ["increased by", "decreased by", "increased by", "decreased by"],
    },
    {
        "item": "a pound of ground beef",
        "base_price": 5.00,
        "changes": ["increased by", "decreased by", "increased by", "decreased by"],
    },
    {
        "item": "a loaf of bread",
        "base_price": 3.25,
        "changes": ["decreased by", "increased by", "increased by", "decreased by"],
    },
]

CONTEXTS_7AF2_UNIT_PRICE = [
    {"item": "tomatoes", "unit": "pound", "unit_plural": "pounds"},
    {"item": "apples", "unit": "pound", "unit_plural": "pounds"},
    {"item": "cheese", "unit": "pound", "unit_plural": "pounds"},
    {"item": "fabric", "unit": "yard", "unit_plural": "yards"},
    {"item": "ribbon", "unit": "foot", "unit_plural": "feet"},
    {"item": "chicken", "unit": "pound", "unit_plural": "pounds"},
]

CONTEXTS_7AF2_FRACTION_WORK = [
    {
        "setup": "{name} needs to mow {frac_of} of a {total}-acre field. {name} can mow {rate_frac} of an acre every {time_per} minutes.",
        "question": "How many minutes will it take {name} to finish mowing?",
    },
    {
        "setup": "{name} is painting {frac_of} of a {total}-foot fence. {name} can paint {rate_frac} of a foot every {time_per} minutes.",
        "question": "How many minutes will it take {name} to finish painting?",
    },
    {
        "setup": "{name} is reading {frac_of} of a {total}-page book. {name} reads {rate_frac} of a page every {time_per} seconds.",
        "question": "How many seconds will it take {name} to finish reading?",
    },
]


# ============================================================
# CONTEXTS FOR 7.AF.3 — TWO-STEP EQUATIONS
# ============================================================

CONTEXTS_7AF3_PX_PLUS_Q = [
    # px + q = r form: "unit price × quantity + flat fee = total"
    {
        "setup": "{name} buys {var} shirts at ${p} each and pays a ${q} shipping fee. The total cost is ${r}.",
        "question": "How many shirts did {name} buy?",
        "equation_form": "{p}{var} + {q} = {r}",
        "var_letter": "s",
    },
    {
        "setup": "{name} pays ${p} per class at a gym, plus a ${q} monthly membership fee. After {var} classes in one month, {name} has paid ${r} total.",
        "question": "How many classes did {name} attend?",
        "equation_form": "{p}{var} + {q} = {r}",
        "var_letter": "c",
    },
    {
        "setup": "A plumber charges ${q} for a house visit plus ${p} per hour of work. The total bill is ${r}.",
        "question": "How many hours did the plumber work?",
        "equation_form": "{p}{var} + {q} = {r}",
        "var_letter": "h",
    },
    {
        "setup": "{name} rents a bicycle for ${q} plus ${p} per hour. The total rental cost is ${r}.",
        "question": "How many hours did {name} rent the bicycle?",
        "equation_form": "{p}{var} + {q} = {r}",
        "var_letter": "h",
    },
    {
        "setup": "A taxi ride costs ${q} base fare plus ${p} per mile. {name}'s ride cost ${r}.",
        "question": "How many miles was the taxi ride?",
        "equation_form": "{p}{var} + {q} = {r}",
        "var_letter": "m",
    },
    {
        "setup": "{name} has ${q} in savings. {name} earns ${p} per hour at a part-time job. After working some hours, {name} has ${r} total.",
        "question": "How many hours did {name} work?",
        "equation_form": "{p}{var} + {q} = {r}",
        "var_letter": "h",
    },
]

CONTEXTS_7AF3_PAREN = [
    # p(x + q) = r form
    {
        "setup": "A group of {p} friends each brought some snacks plus {q} drinks to a party. The group brought {r} items in total.",
        "question": "How many snacks did each friend bring?",
        "equation_form": "{p}({var} + {q}) = {r}",
        "var_letter": "s",
    },
    {
        "setup": "{name} is making {p} identical gift bags. Each bag has some candy plus {q} stickers. {name} uses {r} items in total.",
        "question": "How many pieces of candy are in each bag?",
        "equation_form": "{p}({var} + {q}) = {r}",
        "var_letter": "c",
    },
    {
        "setup": "There are {p} rows of chairs in an auditorium. Each row has some folding chairs plus {q} permanent seats. There are {r} seats total.",
        "question": "How many folding chairs are in each row?",
        "equation_form": "{p}({var} + {q}) = {r}",
        "var_letter": "f",
    },
]

CONTEXTS_7AF3_SUB = [
    # a - bx = c form: "starting amount, decreasing by b per unit, ends at c".
    # Here {r} = starting amount, {p} = amount removed per unit, {q} = amount left.
    {
        "setup": "{name} has ${r} on a gift card and spends ${p} on each movie ticket. After buying {var} tickets, ${q} is left on the card.",
        "question": "How many movie tickets did {name} buy?",
        "equation_form": "{r} - {p}{var} = {q}",
        "var_letter": "t",
    },
    {
        "setup": "A water tank holds {r} liters and drains {p} liters each hour. After {var} hours, {q} liters remain.",
        "question": "For how many hours did the tank drain?",
        "equation_form": "{r} - {p}{var} = {q}",
        "var_letter": "h",
    },
    {
        "setup": "{name} begins a road trip with {r} miles left to drive and covers {p} miles each hour. After {var} hours, {q} miles remain.",
        "question": "How many hours did {name} drive?",
        "equation_form": "{r} - {p}{var} = {q}",
        "var_letter": "h",
    },
    {
        "setup": "{name} has ${r} in a checking account and pays ${p} for each monthly subscription. After paying for {var} subscriptions, ${q} remains.",
        "question": "How many subscriptions did {name} pay for?",
        "equation_form": "{r} - {p}{var} = {q}",
        "var_letter": "s",
    },
    {
        "setup": "A delivery van starts with {r} gallons of fuel and uses {p} gallons on each delivery. After {var} deliveries, {q} gallons remain.",
        "question": "How many deliveries did the van make?",
        "equation_form": "{r} - {p}{var} = {q}",
        "var_letter": "d",
    },
]


# ============================================================
# CONTEXTS FOR 7.AF.4 — TWO-STEP INEQUALITIES
# ============================================================

# Subtraction inequalities of the form a - bx {op} c: a starting amount that
# decreases by b per unit and must stay at/above a threshold. Isolating x from
# -bx flips the inequality. {r} = starting amount (a), {p} = removed per unit
# (b), {q} = threshold (c).
CONTEXTS_7AF4_INEQUALITY_SUB = [
    {
        "setup": "{name} has ${r} on a gift card and spends ${p} on each arcade game. {name} wants to keep at least ${q} on the card.",
        "question": "Write an inequality for {var}, the number of games {name} can play.",
        "op": ">=",
        "var_letter": "g",
    },
    {
        "setup": "A truck starts a trip with {r} gallons of fuel and burns {p} gallons each hour. At least {q} gallons must remain for the return trip.",
        "question": "Write an inequality for {var}, the number of hours the truck can drive.",
        "op": ">=",
        "var_letter": "h",
    },
    {
        "setup": "{name} has {r} GB of data this month, and each movie streamed uses {p} GB. {name} wants more than {q} GB left to avoid slowdowns.",
        "question": "Write an inequality for {var}, the number of movies {name} can stream.",
        "op": ">",
        "var_letter": "m",
    },
    {
        "setup": "{name}'s phone is at {r} percent battery and drops {p} percent for each hour of video. {name} needs at least {q} percent remaining.",
        "question": "Write an inequality for {var}, the number of hours {name} can watch.",
        "op": ">=",
        "var_letter": "h",
    },
]

CONTEXTS_7AF4_INEQUALITY = [
    {
        "setup": "{name} is saving for a concert ticket that costs at least ${r}. {name} already has ${q} and earns ${p} per hour.",
        "question": "Write an inequality to represent {var}, the number of hours {name} must work.",
        "form": "{p}{var} + {q} >= {r}",
        "op": ">=",
        "var_letter": "h",
    },
    {
        "setup": "A water bottle company needs to fill bottles for an order of at least {r} ounces. The machine has already filled {q} ounces and fills at a rate of {p} ounces per minute.",
        "question": "Write an inequality to represent {var}, the number of minutes needed.",
        "form": "{p}{var} + {q} >= {r}",
        "op": ">=",
        "var_letter": "m",
    },
    {
        "setup": "{name} wants to spend less than ${r} at a store. {name} has a ${q} coupon and each item costs ${p}.",
        "question": "Write an inequality to represent {var}, the number of items {name} can buy.",
        "form": "{p}{var} - {q} < {r}",
        "op": "<",
        "var_letter": "n",
    },
    {
        "setup": "A parking garage charges ${q} plus ${p} per hour. {name} has at most ${r} to spend on parking.",
        "question": "Write an inequality to represent {var}, the number of hours {name} can park.",
        "form": "{p}{var} + {q} <= {r}",
        "op": "<=",
        "var_letter": "h",
    },
]


# ============================================================
# CONTEXTS FOR 7.AF.5 — SLOPE & RATE OF CHANGE
# ============================================================

CONTEXTS_7AF5_LINEAR = [
    {
        "desc": "{name} earns ${rate} per hour at a part-time job",
        "x_label": "Hours", "y_label": "Earnings ($)",
    },
    {
        "desc": "A car travels at a constant speed of {rate} miles per hour",
        "x_label": "Hours", "y_label": "Distance (miles)",
    },
    {
        "desc": "A plant grows {rate} centimeters per week",
        "x_label": "Weeks", "y_label": "Height (cm)",
    },
    {
        "desc": "A pool fills at a rate of {rate} gallons per minute",
        "x_label": "Minutes", "y_label": "Water (gallons)",
    },
    {
        "desc": "A printer prints {rate} pages per minute",
        "x_label": "Minutes", "y_label": "Pages printed",
    },
]

CONTEXTS_7AF5_NONLINEAR = [
    {
        "desc": "A ball is thrown upward — its height changes at a varying rate",
        "x_label": "Seconds", "y_label": "Height (feet)",
    },
    {
        "desc": "A population of bacteria doubles every hour",
        "x_label": "Hours", "y_label": "Bacteria count",
    },
    {
        "desc": "The value of a car decreases by 5% each year",
        "x_label": "Years", "y_label": "Value ($)",
    },
    {
        "desc": "{name} runs faster at the start and slows down as the race continues",
        "x_label": "Minutes", "y_label": "Total distance (miles)",
    },
]

CONTEXTS_7AF5_SLOPE_INTERP = [
    {
        "context": "A wheelchair ramp has a slope of {slope}.",
        "interp": "For every {den} feet of horizontal distance, the ramp rises {num} foot.",
    },
    {
        "context": "A hiking trail has a slope of {slope}.",
        "interp": "For every {den} feet of horizontal distance, the trail rises {num} feet.",
    },
    {
        "context": "A roof has a pitch (slope) of {slope}.",
        "interp": "For every {den} feet of horizontal distance, the roof rises {num} feet.",
    },
]


# ============================================================
# CONTEXTS FOR 7.AF.6 — GRAPHING LINES
# ============================================================

CONTEXTS_7AF6_REAL_WORLD_SLOPE = [
    {
        "desc": "A delivery driver delivers {num} packages in {den} hours.",
        "rate_unit": "packages per hour",
    },
    {
        "desc": "A factory produces {num} widgets every {den} minutes.",
        "rate_unit": "widgets per minute",
    },
    {
        "desc": "A student reads {num} pages in {den} minutes.",
        "rate_unit": "pages per minute",
    },
    {
        "desc": "{name} types {num} words every {den} seconds.",
        "rate_unit": "words per second",
    },
    {
        "desc": "A garden hose fills a pool at {num} gallons every {den} minutes.",
        "rate_unit": "gallons per minute",
    },
]


# ============================================================
# 8th Grade Contexts
# ============================================================

CONTEXTS_8AF1_EQUATION = [
    {
        "template": "{name} joins a gym that charges a one-time enrollment fee of ${flat} plus ${rate} per month. After {x} months, {name} has paid a total of ${total}. How many months has {name} been a member?",
        "equation": "{rate}x + {flat} = {total}",
        "var_letter": "x",
    },
    {
        "template": "A plumber charges ${flat} for a house call plus ${rate} per hour of labor. The total bill was ${total}. How many hours did the plumber work?",
        "equation": "{rate}x + {flat} = {total}",
        "var_letter": "x",
    },
    {
        "template": "{name} is saving money. {name} already has ${flat} saved and adds ${rate} each week. How many weeks until {name} has ${total}?",
        "equation": "{rate}x + {flat} = {total}",
        "var_letter": "x",
    },
    {
        "template": "A phone plan costs ${flat} per month plus ${rate} per gigabyte of data. This month's bill was ${total}. How many gigabytes of data were used?",
        "equation": "{rate}x + {flat} = {total}",
        "var_letter": "x",
    },
    {
        "template": "{name} rents a car for ${flat} per day plus ${rate} per mile driven. The total cost for one day was ${total}. How many miles did {name} drive?",
        "equation": "{rate}x + {flat} = {total}",
        "var_letter": "x",
    },
    {
        "template": "A streaming service charges ${flat} per month plus ${rate} for each movie rented. {name}'s bill this month was ${total}. How many movies did {name} rent?",
        "equation": "{rate}x + {flat} = {total}",
        "var_letter": "x",
    },
]

CONTEXTS_8AF1_INEQUALITY = [
    {
        "template": "{name} earns ${rate} per hour tutoring and already has ${flat} in savings. {name} wants to save at least ${goal}. How many hours must {name} work?",
        "inequality": "{rate}x + {flat} >= {goal}",
        "op": ">=",
    },
    {
        "template": "{name} has ${flat} to spend at a fair. Rides cost ${rate} each. What is the maximum number of rides {name} can take?",
        "inequality": "{rate}x <= {flat}",
        "op": "<=",
    },
    {
        "template": "A parking garage charges ${flat} for the first hour and ${rate} for each additional hour. {name} has ${goal} to spend. How many additional hours can {name} park?",
        "inequality": "{rate}x + {flat} <= {goal}",
        "op": "<=",
    },
    {
        "template": "{name} sells lemonade for ${rate} per cup. Materials cost ${flat}. How many cups must {name} sell to make a profit greater than ${goal}?",
        "inequality": "{rate}x - {flat} > {goal}",
        "op": ">",
    },
]

CONTEXTS_8AF6_LINEAR = [
    {
        "desc": "A phone plan costs ${b} per month plus ${m} per gigabyte of data used.",
        "x_label": "Gigabytes", "y_label": "Cost ($)",
        "m_meaning": "cost per gigabyte of data",
        "b_meaning": "base monthly fee",
    },
    {
        "desc": "{name} is filling a pool that already has {b} gallons. Water flows in at {m} gallons per minute.",
        "x_label": "Minutes", "y_label": "Water (gallons)",
        "m_meaning": "gallons added per minute",
        "b_meaning": "initial amount of water in the pool",
    },
    {
        "desc": "A taxi ride costs ${b} base fare plus ${m} per mile.",
        "x_label": "Miles", "y_label": "Cost ($)",
        "m_meaning": "cost per mile",
        "b_meaning": "base fare",
    },
    {
        "desc": "{name} starts with {b} stickers and collects {m} new stickers each day.",
        "x_label": "Days", "y_label": "Stickers",
        "m_meaning": "stickers collected per day",
        "b_meaning": "starting number of stickers",
    },
    {
        "desc": "A candle is {b} inches tall and burns down {m} inches per hour.",
        "x_label": "Hours", "y_label": "Height (inches)",
        "m_meaning": "inches the candle melts per hour",
        "b_meaning": "initial height of the candle",
    },
    {
        "desc": "{name} has ${b} in a savings account and deposits ${m} each week.",
        "x_label": "Weeks", "y_label": "Balance ($)",
        "m_meaning": "dollars saved per week",
        "b_meaning": "initial savings balance",
    },
    {
        "desc": "A plant is {b} centimeters tall and grows {m} centimeters per week.",
        "x_label": "Weeks", "y_label": "Height (cm)",
        "m_meaning": "growth per week in centimeters",
        "b_meaning": "initial height of the plant",
    },
    {
        "desc": "{name} reads at a rate of {m} pages per hour and has already read {b} pages.",
        "x_label": "Hours", "y_label": "Pages Read",
        "m_meaning": "pages read per hour",
        "b_meaning": "pages already read before starting",
    },
]

CONTEXTS_8AF8_SYSTEM = [
    {
        "desc": "Two cell phone plans",
        "func_a": "Plan A charges ${b1} per month plus ${m1} per text message",
        "func_b": "Plan B charges ${b2} per month plus ${m2} per text message",
        "x_label": "text messages", "y_label": "monthly cost",
    },
    {
        "desc": "Two car rental companies",
        "func_a": "Company A charges ${b1} per day plus ${m1} per mile",
        "func_b": "Company B charges ${b2} per day plus ${m2} per mile",
        "x_label": "miles driven", "y_label": "total cost",
    },
    {
        "desc": "Two internet providers",
        "func_a": "Provider A charges ${b1} installation fee plus ${m1} per month",
        "func_b": "Provider B charges ${b2} installation fee plus ${m2} per month",
        "x_label": "months", "y_label": "total cost",
    },
    {
        "desc": "Two gym memberships",
        "func_a": "{name}'s gym charges ${b1} enrollment plus ${m1} per month",
        "func_b": "The other gym charges ${b2} enrollment plus ${m2} per month",
        "x_label": "months", "y_label": "total cost",
    },
]


# ============================================================
# CONTEXTS FOR 6.NS.1 — POSITIVE/NEGATIVE NUMBERS
# ============================================================

CONTEXTS_6NS1 = [
    {
        "context": "temperature",
        "positive": "{val} degrees above zero",
        "negative": "{val} degrees below zero",
        "zero_meaning": "Zero degrees means the freezing point of water.",
        "unit": "degrees",
    },
    {
        "context": "elevation",
        "positive": "{val} feet above sea level",
        "negative": "{val} feet below sea level",
        "zero_meaning": "Zero represents sea level.",
        "unit": "feet",
    },
    {
        "context": "money",
        "positive": "a deposit of ${val}",
        "negative": "a withdrawal of ${val}",
        "zero_meaning": "Zero means the account balance is exactly $0 - neither in debt nor in credit.",
        "unit": "dollars",
    },
    {
        "context": "football",
        "positive": "a gain of {val} yards",
        "negative": "a loss of {val} yards",
        "zero_meaning": "Zero means the team stayed at the line of scrimmage - no gain or loss.",
        "unit": "yards",
    },
    {
        "context": "time",
        "positive": "{val} seconds after launch",
        "negative": "{val} seconds before launch (countdown)",
        "zero_meaning": "Zero represents the moment of launch.",
        "unit": "seconds",
    },
    {
        "context": "floors",
        "positive": "floor {val} (above ground)",
        "negative": "{val} floors underground (basement)",
        "zero_meaning": "Zero represents ground level.",
        "unit": "floors",
    },
]


# ============================================================
# CONTEXTS FOR 6.NS.4 — FRACTION/DECIMAL WORD PROBLEMS
# ============================================================

CONTEXTS_6NS4 = [
    {
        "template": "{name} bought {a} pounds of apples and {b} pounds of oranges. How many total pounds of fruit did {name} buy?",
        "operation": "add", "unit": "pounds",
    },
    {
        "template": "{name} had {a} yards of fabric and used {b} yards for a project. How much fabric does {name} have left?",
        "operation": "subtract", "unit": "yards",
    },
    {
        "template": "A recipe calls for {a} cups of flour. {name} wants to make {b} batches. How much flour does {name} need?",
        "operation": "multiply", "unit": "cups",
    },
    {
        "template": "{name} has {a} pounds of trail mix to divide equally into {b} bags. How much trail mix goes in each bag?",
        "operation": "divide", "unit": "pounds",
    },
    {
        "template": "{name} ran {a} miles on Monday and {b} miles on Tuesday. How many total miles did {name} run?",
        "operation": "add", "unit": "miles",
    },
    {
        "template": "{name} had ${a} and spent ${b} on a book. How much money does {name} have left?",
        "operation": "subtract", "unit": "dollars",
    },
]


# ============================================================
# CONTEXTS FOR 6.RP.2 — UNIT RATE
# ============================================================

CONTEXTS_6RP2 = [
    {"template": "{name} drove {b} miles in {a} hours.", "unit": "miles per hour", "rate_label": "speed"},
    {"template": "{name} earned ${b} for {a} hours of work.", "unit": "dollars per hour", "rate_label": "hourly wage"},
    {"template": "A store sells {b} apples for ${a}.", "unit": "apples per dollar", "rate_label": "value"},
    {"template": "{name} read {b} pages in {a} minutes.", "unit": "pages per minute", "rate_label": "reading rate"},
    {"template": "A printer printed {b} pages in {a} minutes.", "unit": "pages per minute", "rate_label": "print speed"},
    {"template": "{name} typed {b} words in {a} minutes.", "unit": "words per minute", "rate_label": "typing speed"},
]


# ============================================================
# CONTEXTS FOR 6.RP.4 — RATIO WORD PROBLEMS
# ============================================================

CONTEXTS_6RP4 = [
    {"template": "A recipe uses {a} cups of flour for every {b} cups of sugar.", "item_a": "flour", "item_b": "sugar", "unit": "cups"},
    {"template": "For every {a} red marbles, there are {b} blue marbles.", "item_a": "red marbles", "item_b": "blue marbles", "unit": "marbles"},
    {"template": "{name} mixes {a} parts paint with {b} parts water.", "item_a": "paint", "item_b": "water", "unit": "parts"},
    {"template": "A bouquet has {a} roses for every {b} daisies.", "item_a": "roses", "item_b": "daisies", "unit": "flowers"},
    {"template": "For every {a} boys in the class, there are {b} girls.", "item_a": "boys", "item_b": "girls", "unit": "students"},
    {"template": "{name} uses {a} scoops of lemonade mix for every {b} cups of water.", "item_a": "lemonade mix", "item_b": "water", "unit": "scoops/cups"},
]


# ============================================================
# CONTEXTS FOR 6.RP.5 — PROPORTIONAL RELATIONSHIPS
# ============================================================

CONTEXTS_6RP5 = [
    {"desc": "{name} sells lemonade for ${rate} per cup.", "x_label": "cups sold", "y_label": "earnings ($)", "var": "y = {rate}x"},
    {"desc": "A cat eats {rate} ounces of food per day.", "x_label": "days", "y_label": "food eaten (oz)", "var": "y = {rate}x"},
    {"desc": "{name} earns ${rate} per hour walking dogs.", "x_label": "hours", "y_label": "earnings ($)", "var": "y = {rate}x"},
    {"desc": "A car uses {rate} gallons of gas per mile.", "x_label": "miles", "y_label": "gas used (gal)", "var": "y = {rate}x"},
]


# ============================================================
# CONTEXTS FOR 7.NS.1 — SIGNED NUMBER ADDITION
# ============================================================

CONTEXTS_7NS1 = [
    {"template": "The temperature was {a} degrees. It changed by {b} degrees. What is the new temperature?", "unit": "degrees"},
    {"template": "{name}'s bank balance was ${a}. After a transaction of ${b}, what is the new balance?", "unit": "dollars"},
    {"template": "A submarine was at {a} feet. It moved {b} feet. What is its new depth?", "unit": "feet"},
    {"template": "{name} was at floor {a} in a building. {name} went {b} floors. What floor is {name} on now?", "unit": "floors"},
    {"template": "A football team was at the {a}-yard line. The next play gained {b} yards. Where is the team now?", "unit": "yards"},
    {"template": "{name} had a score of {a} points. {name} earned {b} more points. What is {name}'s score now?", "unit": "points"},
]


# ============================================================
# CONTEXTS FOR 7.NS.2 — DISTANCE / ABSOLUTE VALUE
# ============================================================

CONTEXTS_7NS2 = [
    {"template": "The high temperature was {a} degrees and the low was {b} degrees. What is the temperature difference?", "unit": "degrees"},
    {"template": "City A is at elevation {a} feet and City B is at {b} feet. What is the difference in elevation?", "unit": "feet"},
    {"template": "Point A is at position {a} and Point B is at position {b} on a number line. How far apart are they?", "unit": "units"},
    {"template": "{name}'s score was {a} and the opponent's score was {b}. How many points apart are they?", "unit": "points"},
]


# ============================================================
# CONTEXTS FOR 7.NS.6 — PERFECT SQUARES / AREA
# ============================================================

CONTEXTS_7NS6 = [
    {"template": "{name} has a square garden with an area of {sq} square feet. What is the side length?", "unit": "feet"},
    {"template": "A square tile has an area of {sq} square inches. What is the side length?", "unit": "inches"},
    {"template": "{name} is building a square sandbox with area {sq} square feet. What side length does {name} need?", "unit": "feet"},
    {"template": "A square painting has an area of {sq} square centimeters. What is the side length?", "unit": "centimeters"},
]


# ============================================================
# CONTEXTS FOR 7.RP.1 — UNIT RATE / CONSTANT OF PROPORTIONALITY
# ============================================================

CONTEXTS_7RP1 = [
    {"desc": "{name} drives {total} miles in {hours} hours.", "x_label": "Hours", "y_label": "Miles", "unit": "miles per hour"},
    {"desc": "A gym membership costs ${total} for {months} months.", "x_label": "Months", "y_label": "Cost ($)", "unit": "dollars per month"},
    {"desc": "{name} buys {items} items for ${total}.", "x_label": "Items", "y_label": "Cost ($)", "unit": "dollars per item"},
    {"desc": "A machine produces {items} widgets in {hours} hours.", "x_label": "Hours", "y_label": "Widgets", "unit": "widgets per hour"},
    {"desc": "{name} earns ${total} for {hours} hours of work.", "x_label": "Hours", "y_label": "Earnings ($)", "unit": "dollars per hour"},
    {"desc": "A printer uses {items} sheets for {pages} pages.", "x_label": "Pages", "y_label": "Sheets", "unit": "sheets per page"},
]


# ============================================================
# CONTEXTS FOR 7.RP.2 — PERCENT PROBLEMS
# ============================================================

CONTEXTS_7RP2 = [
    {"type": "tax", "template": "{name} buys an item for ${price}. Sales tax is {rate}%. What is the total cost?"},
    {"type": "tip", "template": "{name} eats at a restaurant. The bill is ${price}. {name} leaves a {rate}% tip. What is the tip amount?"},
    {"type": "discount", "template": "A ${price} jacket is on sale for {rate}% off. What is the sale price?"},
    {"type": "markup", "template": "A store buys an item for ${price} and marks it up {rate}%. What is the selling price?"},
    {"type": "increase", "template": "A city's population was {price}. It increased by {rate}%. What is the new population?"},
    {"type": "decrease", "template": "A car worth ${price} depreciated by {rate}%. What is the new value?"},
    {"type": "interest", "template": "{name} deposits ${price} in a savings account earning {rate}% simple interest per year. How much interest after 1 year?"},
    {"type": "total", "template": "{name} buys a meal for ${price}. Tax is {rate1}% and tip is {rate2}%. What is the total cost?"},
]


# ============================================================
# CONTEXTS FOR 7.RP.3 — PROPORTIONAL RELATIONSHIPS
# ============================================================

CONTEXTS_7RP3 = [
    {"desc": "{name} makes banana bread using {rate} cups of sugar per loaf.", "x_label": "Loaves", "y_label": "Sugar (cups)"},
    {"desc": "Carnival tickets cost ${rate} each.", "x_label": "Tickets", "y_label": "Cost ($)"},
    {"desc": "Granola costs ${rate} per pound.", "x_label": "Pounds", "y_label": "Cost ($)"},
    {"desc": "{name} walks {rate} miles per hour.", "x_label": "Hours", "y_label": "Miles"},
]


# ============================================================
# CONTEXTS FOR 8.NS.4 — MULTI-STEP RATIONAL PROBLEMS
# ============================================================

CONTEXTS_8NS4 = [
    {"template": "{name} buys {n} items at ${price} each, with a {rate}% discount. What is the total cost?", "type": "discount_shopping"},
    {"template": "{name} earns ${rate1} per hour for {h1} hours and ${rate2} per hour for {h2} hours. What are {name}'s total earnings?", "type": "wages"},
    {"template": "A recipe serves {base} people. {name} needs to serve {target} people. If the recipe calls for {amount} cups of flour, how much flour does {name} need?", "type": "recipe_scaling"},
    {"template": "{name} has ${start}. {name} spends {pct}% on supplies and then earns ${earn} more. How much does {name} have now?", "type": "money_steps"},
    {"template": "A store marks up items by {rate1}%, then offers a {rate2}% sale. If the wholesale price is ${price}, what is the sale price?", "type": "markup_discount"},
    {"template": "{name} invests ${price} at {rate}% simple interest for {years} years. What is the total value?", "type": "simple_interest"},
]
