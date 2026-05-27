def get_competency_rating(score):
    if 30 <= score <= 35:
        return "Excellent mentor skills; you could coach others; concentrate improvement efforts on fine-tuning your style with particular mentees"
    elif 25 <= score <= 29:
        return "Very good skills; continue to polish those skills that will make you even more effective and desirable as a mentor"
    elif 15 <= score <= 24:
        return "Good skills; you need to work on certain areas of improvements to ensure you are an effective and desirable mentor"
    elif 10 <= score <= 14:
        return "Adequate mentor skills; work on your less-developed skills in order to acquire strong mentees and have better relationships with them"
    else:
        return "You will benefit from coaching and practice on mentor skills; acquire training or coaching, and observe others who have strong skill"
