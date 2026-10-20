# Exam {{ exam_number }} - Answer Distributions

*{{ total_students }} students. Ordered by Exam A question number. Percentages combine Exam A and Exam B students. ✓ = correct answer.*

### Question Mapping

{% if question_map %}
{# An empty spacer column separates each Exam B / Exam A pair. #}
|{% for _ in question_map[0] %} Exam B | Exam A |{% if not loop.last %} |{% endif %}{% endfor %}

|{% for _ in question_map[0] %}:-:|:-:|{% if not loop.last %}--|{% endif %}{% endfor %}

{% for row in question_map %}
|{% for m in row %} {{ m.b_number }} | {{ m.a_number }} |{% if not loop.last %} |{% endif %}{% endfor %}

{% endfor %}
{% endif %}

---

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

---

{% endfor %}
