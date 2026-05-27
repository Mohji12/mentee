#!/usr/bin/env python3
"""
Test script to debug SWOT analysis parsing
Run this script to test the parse_swot_analysis function with sample data
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from utils.analysis import parse_swot_analysis

def test_swot_parsing():
    """Test the SWOT parsing function with sample data"""
    
    # Sample SWOT analysis text (similar to what might be generated)
    sample_swot = """
**Professional Aspirations**
The student aspires to become a software engineer with a focus on machine learning and artificial intelligence. They are particularly interested in developing solutions that can help solve real-world problems in healthcare and education.

**Skills/Interests/Hobbies**
The student enjoys programming in Python and JavaScript, has a keen interest in data science, and participates in coding competitions. They also enjoy reading technical blogs and contributing to open-source projects.

**Strengths**
- Strong analytical thinking and problem-solving skills
- Excellent programming abilities in multiple languages
- Good communication skills and team collaboration
- Self-motivated and eager to learn new technologies

**Weaknesses**
- Limited practical work experience in professional settings
- Sometimes struggles with time management on large projects
- Needs improvement in public speaking and presentation skills

**Opportunities**
- Access to various online learning platforms and courses
- University career services and internship programs
- Local tech meetups and networking events
- Open source projects for gaining experience

**Threats**
- Rapid changes in technology requiring constant learning
- High competition in the job market
- Economic uncertainties affecting tech hiring
- Potential skill obsolescence without continuous learning

**Detailed Summary Analysis**
The student shows strong potential for success in the technology field with their analytical mindset and programming skills. To maximize their opportunities, they should focus on gaining practical experience through internships and projects while improving their soft skills. The key is to maintain a balance between technical learning and professional development.

**Activities**
**Short Term (0-2 Months):**
1. Complete an online machine learning course
2. Build a personal portfolio website
3. Join local programming meetups

**Mid Term (3-6 Months):**
1. Apply for summer internships
2. Contribute to open source projects
3. Attend tech conferences

**Long Term (7-12 Months):**
1. Secure a software engineering internship
2. Develop a specialized skill in AI/ML
3. Build a professional network in the industry
"""

    print("🧪 Testing SWOT Analysis Parsing")
    print("=" * 50)
    
    # Test the parsing function
    result = parse_swot_analysis(sample_swot)
    
    print("📊 Parsing Results:")
    print("-" * 30)
    for key, value in result.items():
        print(f"{key}: {value[:100]}{'...' if len(value) > 100 else ''}")
        print()
    
    # Check if any fields are "Not specified"
    not_specified = [k for k, v in result.items() if v == "Not specified"]
    if not_specified:
        print(f"⚠️  Warning: The following fields could not be parsed: {', '.join(not_specified)}")
    else:
        print("✅ All fields parsed successfully!")
    
    return result

if __name__ == "__main__":
    test_swot_parsing()
