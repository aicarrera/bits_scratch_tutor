import { useEffect, useState } from "react";

import { Assent } from "./pages/Assent";
import { Chat } from "./pages/Chat";
import { Feedback } from "./pages/Feedback";
import { GameSelection } from "./pages/GameSelection";
import { Welcome } from "./pages/Welcome";
import type { Conversation, Game, Student } from "./types/api";

type Screen = "welcome" | "assent" | "selection" | "chat" | "feedback";

export default function App() {
  const [screen, setScreen] = useState<Screen>("welcome");
  const [student, setStudent] = useState<Student | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [currentGame, setCurrentGame] = useState<Game | null>(null);
  const [conversation, setConversation] = useState<Conversation | null>(null);

  // Browser tab close → mark session abandoned so it can be resumed next time
  useEffect(() => {
    if (screen !== "chat" || !sessionId) return;
    const sid = sessionId;
    const handleBeforeUnload = () => {
      const apiUrl = (import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000").replace(/\/$/, "");
      navigator.sendBeacon(`${apiUrl}/api/v1/sessions/${sid}/abandon`);
    };
    window.addEventListener("beforeunload", handleBeforeUnload);
    return () => window.removeEventListener("beforeunload", handleBeforeUnload);
  }, [screen, sessionId]);

  const reset = () => {
    setScreen("welcome");
    setStudent(null);
    setSessionId(null);
    setCurrentGame(null);
    setConversation(null);
  };

  // All 3 exit paths (cambiar, salir, finalizar) → feedback first
  const goToFeedback = () => {
    setCurrentGame(null);
    setConversation(null);
    setScreen("feedback");
  };

  const backToSelectionAfterFeedback = () => {
    setSessionId(null);
    setScreen("selection");
  };

  if (screen === "welcome") {
    return (
      <Welcome
        onValidated={(validatedStudent) => {
          setStudent(validatedStudent);
          setScreen("assent");
        }}
      />
    );
  }

  if (screen === "assent" && student) {
    return (
      <Assent
        student={student}
        onAccepted={() => setScreen("selection")}
        onRejected={reset}
      />
    );
  }

  if (screen === "selection" && student) {
    return (
      <GameSelection
        student={student}
        onSelected={(selectedGame, openedSessionId, openedConversation) => {
          setCurrentGame(selectedGame);
          setSessionId(openedSessionId);
          setConversation(openedConversation);
          setScreen("chat");
        }}
      />
    );
  }

  if (screen === "chat" && student && sessionId && currentGame && conversation) {
    return (
      <Chat
        student={student}
        sessionId={sessionId}
        game={currentGame}
        conversation={conversation}
        onConversationUpdated={setConversation}
        onBack={goToFeedback}
        onFinished={goToFeedback}
        onAbandoned={goToFeedback}
      />
    );
  }

  if (screen === "feedback" && student && sessionId) {
    return (
      <Feedback
        student={student}
        sessionId={sessionId}
        onPlayAgain={backToSelectionAfterFeedback}
        onDone={reset}
      />
    );
  }

  return (
    <Welcome
      onValidated={(validatedStudent) => {
        setStudent(validatedStudent);
        setScreen("assent");
      }}
    />
  );
}
