import React, { useState, useEffect } from 'react';
import { ThumbsUp, ThumbsDown, Sparkles, Send, MessageSquare } from 'lucide-react';
import { useAppStore } from '../../stores/useAppStore';

export function ReviewRatingWidget() {
  const { activeProject } = useAppStore();
  const [isOpenFeedback, setIsOpenFeedback] = useState(false);
  const [comment, setComment] = useState('');
  const [reviewState, setReviewState] = useState({
    qualityScore: 175,
    emotion: {
      mood: 'HAPPY',
      emoji: '😄',
      message: 'AI is ready and eager to build!'
    }
  });
  const [toastFeedback, setToastFeedback] = useState('');

  const fetchReviewStats = async () => {
    try {
      const res = await fetch('http://localhost:3001/api/reviews/stats');
      if (res.ok) {
        const data = await res.json();
        setReviewState(data);
      }
    } catch (e) {}
  };

  useEffect(() => {
    fetchReviewStats();
  }, []);

  const handleReview = async (sentiment) => {
    try {
      const res = await fetch('http://localhost:3001/api/reviews/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          projectId: activeProject?.id || '',
          sentiment,
          comment: comment.trim()
        })
      });

      if (res.ok) {
        const data = await res.json();
        setReviewState(data);
        if (sentiment === 'positive') {
          setToastFeedback('🎉 Shukriya! AI bohot khush hua (+50 pts)!');
        } else {
          setToastFeedback('🧐 Feedback mila: AI Deep Research & Correction mode me gaya!');
        }
        setTimeout(() => setToastFeedback(''), 4000);
        setIsOpenFeedback(false);
        setComment('');
      }
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="flex items-center gap-2 relative">
      {/* Toast popup */}
      {toastFeedback && (
        <div className="absolute top-10 right-0 z-50 bg-slate-900 border border-indigo-500/40 text-white px-3 py-1.5 rounded-lg shadow-xl text-xs font-semibold flex items-center gap-1.5 animate-fadeIn">
          <span>{toastFeedback}</span>
        </div>
      )}

      {/* Live AI Emotion Mood Badge */}
      <div 
        className="flex items-center gap-1.5 px-2 py-1 bg-ide-panel border border-indigo-500/30 rounded text-xs text-indigo-300 font-medium cursor-default"
        title={reviewState.emotion.message}
      >
        <span className="text-sm">{reviewState.emotion.emoji}</span>
        <span className="font-semibold text-white">{reviewState.qualityScore} pts</span>
      </div>

      {/* Review Action Buttons */}
      <div className="flex items-center gap-1 bg-ide-panel border border-ide-border rounded p-0.5 text-xs">
        <button
          onClick={() => handleReview('positive')}
          className="p-1 hover:bg-emerald-500/20 text-slate-300 hover:text-emerald-400 rounded transition-colors flex items-center gap-1 text-[11px]"
          title="Acha Kaam Kiya! (+50 pts)"
        >
          <ThumbsUp className="w-3.5 h-3.5 text-emerald-400" />
          <span className="hidden sm:inline">Acha</span>
        </button>

        <button
          onClick={() => setIsOpenFeedback(!isOpenFeedback)}
          className="p-1 hover:bg-rose-500/20 text-slate-300 hover:text-rose-400 rounded transition-colors flex items-center gap-1 text-[11px]"
          title="Bakwas / Improve Karo (-25 pts & Deep Research)"
        >
          <ThumbsDown className="w-3.5 h-3.5 text-rose-400" />
          <span className="hidden sm:inline">Bakwas</span>
        </button>
      </div>

      {/* Criticism & Improvement Popover */}
      {isOpenFeedback && (
        <div className="absolute top-10 right-0 z-40 w-72 bg-ide-panel border border-rose-500/40 rounded-xl shadow-2xl p-3 flex flex-col gap-2">
          <div className="flex items-center justify-between text-xs font-bold text-white">
            <span className="text-rose-400 flex items-center gap-1">
              <span>🧐</span>
              <span>AI Ko Kya Improve Karna Chahiye?</span>
            </span>
            <button 
              onClick={() => setIsOpenFeedback(false)}
              className="text-ide-muted hover:text-white"
            >
              ✕
            </button>
          </div>

          <textarea
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            placeholder="e.g. Colors change karo, search filter fix karo, dark theme better banao..."
            className="w-full h-16 p-2 bg-ide-bg border border-ide-border focus:border-rose-400 rounded text-xs text-white focus:outline-none resize-none"
            autoFocus
          />

          <div className="flex gap-2">
            <button
              onClick={() => handleReview('negative')}
              className="flex-1 py-1 bg-rose-600 hover:bg-rose-500 text-white font-semibold text-xs rounded flex items-center justify-center gap-1 transition-colors"
            >
              <Send className="w-3 h-3" />
              <span>Submit & Start Deep Research</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
