"use client";
import { useState } from "react";

export default function Home() {
  const [messages, setMessages] = useState<
    Array<{ role: "user" | "assistant"; content: string; sources?: string[] }>
  >([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [collection, setCollection] = useState("alltius_rag_chunks_angelone");

  const handleSubmit = async (e: React.FormEvent) => {
    console.log("handleSubmit");
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = input;
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: userMessage }]);
    setIsLoading(true);

    try {
      console.log(process.env.CHAT_API_URL);
      console.log(userMessage);
      console.log(collection);
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_CHAT_API_URL}/chat`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            query: userMessage,
            collection: collection,
          }),
        }
      );

      const data = await response.json();
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: data.answer,
          sources: data.sources,
        },
      ]);
    } catch (error) {
      console.error("Error:", error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen p-4">
      <div className="w-full max-w-md mx-auto mb-4">
        <select
          value={collection}
          onChange={(e) => setCollection(e.target.value)}
          className="w-full p-2 border rounded-lg"
        >
          <option value="alltius_rag_chunks_angelone">Angel One</option>
          <option value="alltius_rag_chunks_insurance">Insurance</option>
        </select>
      </div>

      <div className="flex-1 overflow-auto mb-4 space-y-4 px-12">
        {messages.map((message, index) => (
          <div key={`message-${index}`}>
            <div
              className={`p-4 rounded-lg ${
                message.role === "user"
                  ? "bg-blue-100 ml-auto max-w-[80%]"
                  : "bg-gray-100 mr-auto max-w-[80%]"
              }`}
            >
              {message.content}
            </div>
            {message.sources && (
              <div className="text-sm text-gray-500 mt-1 mr-auto">
                Sources:{" "}
                {message.sources.map((source, i) => (
                  <span key={`source-${index}-${i}`}>
                    <a
                      href={
                        collection === "alltius_rag_chunks_insurance"
                          ? `${process.env.NEXT_PUBLIC_CHAT_API_URL}${source}`
                          : source
                      }
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-500 hover:underline"
                    >
                      {source}
                    </a>
                    {i < (message.sources?.length ?? 0) - 1 && ", "}
                  </span>
                ))}
              </div>
            )}
          </div>
        ))}
        {isLoading && (
          <div className="bg-gray-100 p-4 rounded-lg mr-auto max-w-[80%]">
            Thinking...
          </div>
        )}
      </div>

      <form onSubmit={handleSubmit} className="flex gap-2 px-12">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your message..."
          className="flex-1 p-2 border rounded-lg"
        />
        <button
          type="submit"
          className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
        >
          Send
        </button>
      </form>
    </div>
  );
}
