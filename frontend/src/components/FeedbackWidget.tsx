import React, { useState } from 'react';
import { MessageCircle, X } from 'lucide-react';
import './FeedbackWidget.css';

interface FeedbackWidgetProps {
  className?: string;
}

const FeedbackWidget: React.FC<FeedbackWidgetProps> = ({ className = '' }) => {
  const [isOpen, setIsOpen] = useState(false);

  const handleFeedbackClick = () => {
    // Open Tally.so feedback form in a new window
    window.open(
      'https://tally.so/r/your-feedback-form-id', // Replace with your actual Tally form URL
      '_blank',
      'width=600,height=700,scrollbars=yes,resizable=yes'
    );
  };

  const handleClose = () => {
    setIsOpen(false);
  };

  return (
    <>
      {/* Feedback Button */}
      <div className={`feedback-widget ${className}`}>
        <button
          onClick={handleFeedbackClick}
          className="feedback-button"
          title="Send Feedback"
          aria-label="Send Feedback"
        >
          <MessageCircle size={24} />
        </button>
      </div>

      {/* Feedback Modal */}
      {isOpen && (
        <div className="feedback-modal-overlay" onClick={handleClose}>
          <div className="feedback-modal" onClick={(e) => e.stopPropagation()}>
            <div className="feedback-modal-header">
              <h3 className="feedback-modal-title">Send Feedback</h3>
              <button
                onClick={handleClose}
                className="feedback-modal-close"
                aria-label="Close"
              >
                <X size={20} />
              </button>
            </div>
            
            <div className="feedback-modal-content">
              We'd love to hear your thoughts! Click the button below to share your feedback with us.
            </div>
            
            <div className="feedback-modal-actions">
              <button
                onClick={handleFeedbackClick}
                className="feedback-modal-button primary"
              >
                Open Feedback Form
              </button>
              <button
                onClick={handleClose}
                className="feedback-modal-button secondary"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default FeedbackWidget;