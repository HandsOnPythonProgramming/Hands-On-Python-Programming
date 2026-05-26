import json
import gradio as gr

QUIZ_PATH = "/content/drive/MyDrive/quiz_data/json_data/quiz_10.json"

with open(QUIZ_PATH, "r") as f:
    QUIZ = json.load(f)["quiz"]

def load_question(index):
    q = QUIZ[index]
    return q["question"], q["options"], q["type"], q["id"]

def check_answer(user_answer, index, score):
    q = QUIZ[index]
    correct = q["answer"]
    qtype = q["type"]

    if qtype == "single":
        is_correct = (user_answer == correct)
    else:
        if user_answer is None:
            user_answer = []
        if isinstance(user_answer, str):
            user_answer = [user_answer]
        is_correct = (set(user_answer) == set(correct))

    if is_correct:
        score += 1
        index += 1
        result = "<span style='color: green; font-weight: bold;'>Correct!</span>"
    else:
        result = "<span style='color: red; font-weight: bold;'>Incorrect. Try again.</span>"

    finished = index >= len(QUIZ)
    return result, index, score, finished

with gr.Blocks() as demo:
    gr.HTML("""
    <style>
    .quiz-container {
      text-align: center;
      width: 100%;
    }

    .question-text {
      font-size: 1.6rem !important;
      font-weight: 600;
      text-align: center;
    }

    .answer-options {
      display: flex !important;
      flex-direction: column !important;
      align-items: center !important;
    }

    .answer-options label {
      font-size: 1.1rem !important;
      line-height: 1.0em !important;
      text-align: center;
    }

    .final-score {
      font-size: 1.5rem !important;
      font-weight: 700;
      text-align: center;
      margin-top: 1rem;
    }

    .quiz-button {
      width: 25% !important;
      margin: 0 auto !important;
      display: block !important;
    }
    </style>
    """)
    with gr.Column(elem_classes=["quiz-container"]):
      question = gr.HTML(elem_classes=["question-text"])
      radio = gr.Radio(label="", visible=False, elem_classes=["answer-options"])
      checkbox = gr.CheckboxGroup(label="", visible=False, elem_classes=["answer-options"])
      result = gr.HTML()
      next_btn = gr.Button("Submit", elem_classes=["quiz-button"])

      index = gr.State(0)
      score = gr.State(0)
      qtype_state = gr.State("single")

    def render_question(index):
        qtext, opts, qtype, _ = load_question(index)
        if qtype == "single":
            return (
                gr.update(value=qtext),
                gr.update(choices=opts, visible=True),
                gr.update(choices=[], visible=False),
                qtype
            )
        else:
            return (
                gr.update(value=qtext),
                gr.update(choices=[], visible=False),
                gr.update(choices=opts, visible=True),
                qtype
            )

    demo.load(
        render_question,
        inputs=index,
        outputs=[question, radio, checkbox, qtype_state]
    )

    def handle_submit(radio_ans, checkbox_ans, qtype, index, score):

        if qtype == "restart":
          start_index = 0
          start_score = 0
          qtext, opts, new_qtype, _ = load_question(0)

          if new_qtype == "single":
            return (
                gr.update(value=qtext),
                "",
                gr.update(value=None, choices=opts, visible=True),
                gr.update(value=[], choices=[], visible=False),
                start_index,
                start_score,
                new_qtype,
                gr.update(value="Submit")
            )
          else:
            return (
                gr.update(value=qtext),
                "",
                gr.update(value=None, choices=[], visible=False),
                gr.update(value=[], choices=opts, visible=True),
                start_index,
                start_score,
                new_qtype,
                gr.update(value="Submit")
            )
        user_answer = radio_ans if qtype == "single" else checkbox_ans
        result_text, new_index, new_score, finished = check_answer(user_answer, index, score)

        # CASE 1 — Incorrect (stay on same question)
        if new_index == index:
            qtext, opts, same_qtype, _ = load_question(index)
            if same_qtype == "single":
                return (
                    gr.update(value=qtext),
                    result_text,
                    gr.update(value=None, choices=opts, visible=True),
                    gr.update(value=[], choices=[], visible=False),
                    index,
                    new_score,
                    same_qtype,
                    gr.update(value="Submit")
                )
            else:
                return (
                    gr.update(value=qtext),
                    result_text,
                    gr.update(value=None, choices=[], visible=False),
                    gr.update(value=[], choices=opts, visible=True),
                    index,
                    new_score,
                    same_qtype,
                    gr.update(value="Submit")
                )

        # CASE 2 — Finished
        if finished:
            return (
                gr.update(value="Quiz Complete!"),
                f"{result_text}<div class='final-score'>Final Score: {new_score}/{len(QUIZ)}</div>",
                gr.update(value=None, visible=False),
                gr.update(value=[], visible=False),
                new_index,
                new_score,
                "restart",
                gr.update(value="Restart")
            )

        # CASE 3 — Correct (advance)
        qtext, opts, new_qtype, _ = load_question(new_index)
        if new_qtype == "single":
            return (
                gr.update(value=qtext),
                result_text,
                gr.update(value=None, choices=opts, visible=True),
                gr.update(value=[], choices=[], visible=False),
                new_index,
                new_score,
                new_qtype,
                gr.update(value="Submit")
            )
        else:
            return (
                gr.update(value=qtext),
                result_text,
                gr.update(value=None, choices=[], visible=False),
                gr.update(value=[], choices=opts, visible=True),
                new_index,
                new_score,
                new_qtype,
                gr.update(value="Submit")
            )

    next_btn.click(
        handle_submit,
        inputs=[radio, checkbox, qtype_state, index, score],
        outputs=[question, result, radio, checkbox, index, score, qtype_state, next_btn]
    )
