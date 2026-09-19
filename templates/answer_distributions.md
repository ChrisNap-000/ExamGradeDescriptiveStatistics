# Exam {{ exam_number }} - Answer Distributions

*{{ total_students }} students. Ordered by Exam A question number. Percentages combine Exam A and Exam B students. ✓ = correct answer.*

{% for q in questions %}
### Question {{ q.a_number }} (Exam B: Question {{ q.b_number }})

{{ q.text | md }}

| Option | Answer | % of Students | # of Students |
|:--|:--|--:|--:|
{% for o in q.options %}
{% if o.is_correct %}
| **{{ o.letter }}** | **{{ o.text | md }} ✓** | **{{ o.percent }}%** | **{{ o.count }}** |
{% else %}
| {{ o.letter }} | {{ o.text | md }} | {{ o.percent }}% | {{ o.count }} |
{% endif %}
{% endfor %}
{% if q.no_answer.count %}
| No Answer | | {{ q.no_answer.percent }}% | {{ q.no_answer.count }} |
{% endif %}

&nbsp;

---

{% endfor %}
