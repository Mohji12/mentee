import React, { useState, useEffect, useRef, useCallback } from "react";
import "../assets/css/Chatbot.css";
import { API_BASE_URL } from "../api";

const Chatbot = React.memo(() => {
  const [isOpen, setIsOpen] = useState(false);
  
  // Debug: Log when component renders
  console.log('Chatbot component rendered');
  const [messages, setMessages] = useState([
    { sender: "bot", text: "Hello! I'm your Guide to assist you. Can I know your USN number?" }
  ]);
  const [step, setStep] = useState(1);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [student, setStudent] = useState({
    usn: "",
    name: "",
    email: "",
    phoneno: "",
    program: "",
    query: "",
  });

  const messagesEndRef = useRef(null);

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  const resetChat = () => {
    setMessages([{ sender: "bot", text: "Hello! I'm your Guide to assist you. Can I know your USN number?" }]);
    setStep(1);
    setStudent({ usn: "", name: "", email: "", phoneno: "", program: "", query: "" });
    setInput("");
  };

  const handleSendMessage = async () => {
    if (!input.trim()) return;
    
    console.log("Current Step:", step);
    console.log("Student Data:", student);

    setMessages((prev) => [...prev, { sender: "user", text: input }]);
    const message = input.trim();
    setInput("");
    setLoading(true);

    switch (step) {
      case 1:
        setStudent((prev) => ({ ...prev, usn: message }));
        await checkUSN(message);
        break;
      case 2:
        setStudent((prev) => ({ ...prev, query: message }));
        setMessages((prev) => [...prev, { sender: "bot", text: "Confirming details..." }]);
        displayStudentDetails();
        setStep(3);
        break;
      case 3:
        confirmDetails(message);
        break;
      case 4:
        setStudent((prev) => ({ ...prev, name: message }));
        setMessages((prev) => [...prev, { sender: "bot", text: "Got it! Now enter your email." }]);
        setStep(5);
        break;
      case 5:
        setStudent((prev) => ({ ...prev, email: message }));
        setMessages((prev) => [...prev, { sender: "bot", text: "Now enter your phone number." }]);
        setStep(6);
        break;
      case 6:
        setStudent((prev) => ({ ...prev, phoneno: message }));
        setMessages((prev) => [...prev, { sender: "bot", text: "Now enter your program." }]);
        setStep(7);
        break;
      case 7:
        setStudent((prev) => ({ ...prev, program: message }));
        setMessages((prev) => [...prev, { sender: "bot", text: "Finally, describe your issue." }]);
        setStep(8);
        break;
        case 8:
          setStudent((prev) => {
            const updatedStudent = { ...prev, query: message };
            console.log("Updated Student Data (before submission):", updatedStudent);
            submitNewStudentQuery(updatedStudent); // ✅ Pass updated state explicitly
            return updatedStudent; // ✅ Ensure state is updated
          });
          break;        
    }

    setLoading(false);
  };

  const checkUSN = async (usn) => {
    setMessages((prev) => [...prev, { sender: "bot", text: "Checking USN..." }]);
    try {
      const response = await fetch(`${API_BASE_URL}/check-usn?usn=${usn}`);
      if (!response.ok) throw new Error("Invalid API response");

      const data = await response.json();
      if (data.exists) {
        setStudent((prev) => ({ ...prev, ...data }));

        if (!data.name) {
          setMessages((prev) => [...prev, { sender: "bot", text: "USN found, but no name. Please enter your full name." }]);
          setStep(4);
        } else {
          setMessages((prev) => [...prev, { sender: "bot", text: `Hello ${data.name}, how may I assist you?` }]);
          setStep(2);
        }
      } else {
        setMessages((prev) => [...prev, { sender: "bot", text: "USN not found. Please enter your full name." }]);
        setStep(4);
      }
    } catch (error) {
      console.error("Error checking USN:", error);
      setMessages((prev) => [...prev, { sender: "bot", text: "Error checking USN. Try again." }]);
    }
  };

  const displayStudentDetails = () => {
    setMessages((prev) => [
      ...prev,
      { sender: "bot", text: `Name: ${student.name || "N/A"}` },
      { sender: "bot", text: `Department: ${student.program || "N/A"}` },
      { sender: "bot", text: `Email: ${student.email || "N/A"}` },
      // { sender: "bot", text: `Phone: ${student.phoneno || "N/A"}` },
      { sender: "bot", text: "Type 'Yes' to confirm or 'No' to enter details manually." }
    ]);
  };

  const confirmDetails = (message) => {
    if (message.toLowerCase() === "yes") {
      submitQuery();
    } else {
      setMessages((prev) => [...prev, { sender: "bot", text: "Please enter your name:" }]);
      setStep(4);
    }
  };

  const submitQuery = async () => {
    try {
      await fetch(`${API_BASE_URL}/submit-query/with-usn`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ usn: student.usn, query_issue: student.query }),
      });

      setMessages([{ sender: "bot", text: "Thank you! We have noted your query. We'll be back to you soon. 😊" }]);
      setTimeout(() => { setIsOpen(false); resetChat(); }, 3000);
    } catch (error) {
      console.error("Error submitting query:", error);
    }
  };

  const submitNewStudentQuery = async (studentData) => {
    if (!studentData) {
        console.error("submitNewStudentQuery received undefined data!");
        return;
    }

    const payload = {
        usn: studentData.usn || "",  
        name: studentData.name,
        email: studentData.email,
        phoneno: studentData.phoneno,
        program: studentData.program,
        query_issue: studentData.query,  // ✅ Ensuring correct field name
    };

    console.log("Sending Payload:", payload);  // ✅ Confirm data before sending

    try {
        const response = await fetch(`${API_BASE_URL}/submit-query/new-student`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });

        const data = await response.json();
        console.log("Response:", data);

        if (response.ok) {
            setMessages([{ sender: "bot", text: "Thank you! Your query has been recorded. 😊. We'll get back to you soon." }]);
            setTimeout(() => { setIsOpen(false); resetChat(); }, 3000);
        } else {
            setMessages([{ sender: "bot", text: "Something went wrong. Please try again." }]);
        }
    } catch (error) {
        console.error("Error submitting query:", error);
        setMessages([{ sender: "bot", text: "Network error. Please try again later." }]);
    }
};
  
  return (
    <div>
      <div className="chatbot-icon" onClick={() => setIsOpen(!isOpen)} title="Click to open chatbot">
        <img src="/logo.png" alt="Chatbot" className="chatbot-logo-img" />
      </div>
      {isOpen && (
        <div className="chatbot-window">
          <div className="chatbot-header">
            <span>Your Guide</span>
            <button onClick={() => setIsOpen(false)}>✖</button>
          </div>
          <div className="chatbot-messages">
            {messages.map((msg, index) => (
              <div key={index} className={msg.sender === "bot" ? "bot-message" : "user-message"}>{msg.text}</div>
            ))}
            <div ref={messagesEndRef} />
          </div>
          <div className="chatbot-input">
            <input type="text" placeholder="Type your message..." value={input} onChange={(e) => setInput(e.target.value)} onKeyDown={(e) => e.key === "Enter" && handleSendMessage()} />
            <button onClick={handleSendMessage} disabled={loading}>Send</button>
          </div>
        </div>
      )}
    </div>
  );
});

Chatbot.displayName = 'Chatbot';

export default Chatbot;
