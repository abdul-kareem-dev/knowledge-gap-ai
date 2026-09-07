import { useState } from "react";

function App() {
  const [message, setMessage] = useState("");
  const [questions, setQuestions] = useState([]);
  const [answers, setAnswers] = useState([]);
  const[evaluations, setEvaluation] = useState([]);
  
  const handleAnswerChange = (index, answer) => {
  const updatedAnswers = [...answers];
  updatedAnswers[index] = answer;

  setAnswers(updatedAnswers);
};

  const connectBackend = async () => {
    const response = await fetch("http://127.0.0.1:8000/");
    const data = await response.json();

    setMessage(data.message);
  };
  const generateQuestions = async () => {
    const response = await fetch("http://127.0.0.1:8000/generate-ai-questions");
    const data = await response.json();

    setQuestions(data.questions);
  };

  const submitAnswers = async () => {
  const response = await fetch("http://127.0.0.1:8000/evaluate-answers", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      questions: questions,
      answers: answers,
    }),
  });

  const data = await response.json();

  console.log(data);

  setEvaluation(data.evaluations);
};
  return (
    <div>
      <h1>Knowledge Gap AI</h1>

      <button onClick={connectBackend}>
        Connect to Backend
      </button>

      <button onClick={generateQuestions}>Generate Question</button>

      <p>{message}</p>

      <div>
  {questions.map((question, index) => (
    <div key={index}>
      <p>
       {index + 1}. {question.question}
      </p>

      <textarea
        placeholder="Type your answer here..."
        value={answers[index] || ""}
        onChange={(e) =>
          handleAnswerChange(index, e.target.value)
         }
        />
       </div>
      ))}
      </div>

      <div>
  
</div>

{questions.length > 0 && (
  <button onClick={submitAnswers}>
    Submit Answers
  </button>
)}

{evaluations.length > 0 && (
  <div>
    <h2>Evaluation Results</h2>

    {evaluations.map((evaluation, index) => (
      <div key={index}>
        <h3>Question {index + 1}</h3>

        <p>
          <strong>Score:</strong> {evaluation.score}/100
        </p>

        <p>
          <strong>Understanding:</strong> {evaluation.understanding}
        </p>

        <p>
          <strong>Demonstrated Concepts:</strong>
          {" "}
          {evaluation.demonstrated_concepts.join(", ")}
        </p>

        <p>
          <strong>Missing Concepts:</strong>
          {" "}
          {evaluation.missing_concepts.join(", ")}
        </p>

        <p>
          <strong>Misconceptions:</strong>
          {" "}
          {evaluation.misconceptions.length > 0
            ? evaluation.misconceptions.join(", ")
            : "None"}
        </p>

        <p>
          <strong>Explanation:</strong> {evaluation.explanation}
        </p>

        <hr />
      </div>
    ))}
  </div>
)}

    </div>
  );
}

export default App;