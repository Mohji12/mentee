"""
IBP (Institutional Behaviour Profile) Questions Data
Total: 36 statements with Likert scale 1-5 (Rarely, Occasionally, Sometimes, Often, Always)
"""

IBP_OPTIONS = {
    "1": "Rarely",
    "2": "Occasionally",
    "3": "Sometimes",
    "4": "Often",
    "5": "Always",
}

IBP_QUESTIONS = {
    1: {
        "text": "I always participate actively in all events and activities in the college",
        "options": IBP_OPTIONS.copy(),
    },
    2: {
        "text": "I do not like studies - I prefer studying just before the exams",
        "options": IBP_OPTIONS.copy(),
    },
    3: {
        "text": "I do not feel bad if my faculty questions me on my mistakes even if he is not my professor",
        "options": IBP_OPTIONS.copy(),
    },
    4: {
        "text": "I communicate strong feelings and resentment to my faculty without caring whether this will affect my relationship with them",
        "options": IBP_OPTIONS.copy(),
    },
    5: {
        "text": "I collect all the information that is needed to study, whether it is within or out of the syllabus",
        "options": IBP_OPTIONS.copy(),
    },
    6: {
        "text": "I discuss various ideas with my classmates without working out the details of these ideas",
        "options": IBP_OPTIONS.copy(),
    },
    7: {
        "text": "I respect and follow institutional traditions that seem to give the institution its identity",
        "options": IBP_OPTIONS.copy(),
    },
    8: {
        "text": "I provide my classmates with the solutions to their problems",
        "options": IBP_OPTIONS.copy(),
    },
    9: {
        "text": "I take my classmates' causes and fight for them",
        "options": IBP_OPTIONS.copy(),
    },
    10: {
        "text": "I get angry with my classmates for not acting according to my instructions / suggestions",
        "options": IBP_OPTIONS.copy(),
    },
    11: {
        "text": "I think of new and creative solutions",
        "options": IBP_OPTIONS.copy(),
    },
    12: {
        "text": "I collect information and data even when these are not immediately needed or used",
        "options": IBP_OPTIONS.copy(),
    },
    13: {
        "text": "I help my classmates to become aware of some of their own strengths",
        "options": IBP_OPTIONS.copy(),
    },
    14: {
        "text": "I avoid meeting my faculty if I am not able to fulfill their expectations",
        "options": IBP_OPTIONS.copy(),
    },
    15: {
        "text": "I help my classmates to see the ethical dimensions of some of their actions",
        "options": IBP_OPTIONS.copy(),
    },
    16: {
        "text": "I champion my classmates' causes even if it is wrong socially / ethically",
        "options": IBP_OPTIONS.copy(),
    },
    17: {
        "text": "I think out many alternative solutions to problems before adopting one for action",
        "options": IBP_OPTIONS.copy(),
    },
    18: {
        "text": "I give a lot of new ideas to my classmates",
        "options": IBP_OPTIONS.copy(),
    },
    19: {
        "text": "I accept only those suggestions that appeal to me",
        "options": IBP_OPTIONS.copy(),
    },
    20: {
        "text": "I instruct my classmates in detail about problems and their solutions",
        "options": IBP_OPTIONS.copy(),
    },
    21: {
        "text": "I argue my point of view in meetings / class rooms",
        "options": IBP_OPTIONS.copy(),
    },
    22: {
        "text": "I give clear instructions to my classmates about what should or should not be done",
        "options": IBP_OPTIONS.copy(),
    },
    23: {
        "text": "I try out new things",
        "options": IBP_OPTIONS.copy(),
    },
    24: {
        "text": "I spend my time on specific work to be performed",
        "options": IBP_OPTIONS.copy(),
    },
    25: {
        "text": "I reassure my classmates of my continued help",
        "options": IBP_OPTIONS.copy(),
    },
    26: {
        "text": "I do not express my negative feelings during unpleasant meetings but continue to be bothered by them",
        "options": IBP_OPTIONS.copy(),
    },
    27: {
        "text": "I help my classmates to examine the appropriateness of proposed actions",
        "options": IBP_OPTIONS.copy(),
    },
    28: {
        "text": "I express resentment to the authorities concerned about things that have not been done as promised",
        "options": IBP_OPTIONS.copy(),
    },
    29: {
        "text": "I continuously search for various resources from which needed information can be obtained in order to work out solutions to problems",
        "options": IBP_OPTIONS.copy(),
    },
    30: {
        "text": "I try out new projects or methods without waiting to consolidate the previous one",
        "options": IBP_OPTIONS.copy(),
    },
    31: {
        "text": "I accept help from others and appreciate it",
        "options": IBP_OPTIONS.copy(),
    },
    32: {
        "text": "I encourage my classmates to come to me frequently to seek my advice and help",
        "options": IBP_OPTIONS.copy(),
    },
    33: {
        "text": "I express my feelings and reactions frankly in meetings / class rooms",
        "options": IBP_OPTIONS.copy(),
    },
    34: {
        "text": "I clearly prescribe standards of behavior to be followed in my classes",
        "options": IBP_OPTIONS.copy(),
    },
    35: {
        "text": "I enjoy trying out new ways and see a problem as a challenge",
        "options": IBP_OPTIONS.copy(),
    },
    36: {
        "text": "I work primarily on projects / class room assignments, sometimes at the cost of sensitivity and attention to the feelings of people",
        "options": IBP_OPTIONS.copy(),
    },
}


def get_all_questions():
    """Return all questions as a list for API responses"""
    return [
        {
            "question_number": num,
            "text": data["text"],
            "options": data["options"],
        }
        for num, data in sorted(IBP_QUESTIONS.items())
    ]


def get_question(question_number: int):
    """Get a specific question by number"""
    if question_number not in IBP_QUESTIONS:
        return None
    return {
        "question_number": question_number,
        "text": IBP_QUESTIONS[question_number]["text"],
        "options": IBP_QUESTIONS[question_number]["options"],
    }
