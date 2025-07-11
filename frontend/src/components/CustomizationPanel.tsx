import { Palette, Type, Sticker } from 'lucide-react';
import React, { useState } from 'react';
import './CustomizationPanel.css';

interface VisualSettings {
  backgroundColor: string;
  textColor: string;
  fontFamily: string;
  fontSize: string;
  stickers: Array<{
    id: string;
    type: string;
    position: { x: number; y: number };
  }>;
}

interface CustomizationPanelProps {
  visualSettings: VisualSettings;
  onUpdateSettings: (settings: Partial<VisualSettings>) => void;
}

const CustomizationPanel: React.FC<CustomizationPanelProps> = ({
  visualSettings,
  onUpdateSettings,
}) => {
  const [activeTab, setActiveTab] = useState<'colors' | 'fonts' | 'stickers'>(
    'colors'
  );

  const backgroundColors = [
    '#ffffff',
    '#fdf2f8',
    '#fef3e2',
    '#f0f9ff',
    '#f0fdf4',
    '#faf5ff',
    '#fff1f2',
    '#fffbeb',
    '#f0f0f0',
    '#f8fafc',
  ];

  const textColors = [
    '#000000',
    '#374151',
    '#7c2d12',
    '#be123c',
    '#7c3aed',
    '#0369a1',
    '#047857',
    '#ea580c',
    '#dc2626',
    '#7c2d12',
  ];

  const fontFamilies = [
    'Arial, sans-serif',
    'Georgia, serif',
    'Times New Roman, serif',
    'Helvetica, sans-serif',
    'Verdana, sans-serif',
    'Courier New, monospace',
    'Impact, sans-serif',
    'Comic Sans MS, cursive',
  ];

  const fontSizes = ['14px', '16px', '18px', '20px', '22px', '24px'];

  const stickerTypes = [
    '🌸',
    '🌺',
    '🌻',
    '🌷',
    '🌹',
    '💕',
    '💖',
    '💗',
    '💓',
    '💝',
    '⭐',
    '✨',
    '🌟',
    '💫',
    '🌙',
    '🌈',
    '🦄',
    '👑',
    '💎',
    '🎀',
    '🎵',
    '🎶',
    '🎨',
    '🎭',
    '🎪',
    '🎡',
    '🎢',
    '🎠',
    '🎈',
    '🎉',
  ];

  const handleStickerAdd = (stickerType: string) => {
    const newSticker = {
      id: Date.now().toString(),
      type: stickerType,
      position: { x: Math.random() * 300, y: Math.random() * 300 },
    };

    const newStickers = [...visualSettings.stickers, newSticker];
    onUpdateSettings({ stickers: newStickers });
  };

  const handleStickerRemove = (stickerId: string) => {
    const newStickers = visualSettings.stickers.filter(s => s.id !== stickerId);
    onUpdateSettings({ stickers: newStickers });
  };

  return (
    <div className="customization-panel">
      <div className="panel-header">
        <h3>Customize Your Journal</h3>
        <div className="panel-tabs">
          <button
            className={`tab-button ${activeTab === 'colors' ? 'active' : ''}`}
            onClick={() => setActiveTab('colors')}
          >
            <Palette className="tab-icon" />
            Colors
          </button>
          <button
            className={`tab-button ${activeTab === 'fonts' ? 'active' : ''}`}
            onClick={() => setActiveTab('fonts')}
          >
            <Type className="tab-icon" />
            Fonts
          </button>
          <button
            className={`tab-button ${activeTab === 'stickers' ? 'active' : ''}`}
            onClick={() => setActiveTab('stickers')}
          >
            <Sticker className="tab-icon" />
            Stickers
          </button>
        </div>
      </div>

      <div className="panel-content">
        {activeTab === 'colors' && (
          <div className="colors-section">
            <div className="color-group">
              <h4>Background Color</h4>
              <div className="color-grid">
                {backgroundColors.map(color => (
                  <button
                    key={color}
                    className={`color-option ${visualSettings.backgroundColor === color ? 'selected' : ''}`}
                    style={{ backgroundColor: color }}
                    onClick={() => onUpdateSettings({ backgroundColor: color })}
                  />
                ))}
              </div>
            </div>
            <div className="color-group">
              <h4>Text Color</h4>
              <div className="color-grid">
                {textColors.map(color => (
                  <button
                    key={color}
                    className={`color-option ${visualSettings.textColor === color ? 'selected' : ''}`}
                    style={{ backgroundColor: color }}
                    onClick={() => onUpdateSettings({ textColor: color })}
                  />
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'fonts' && (
          <div className="fonts-section">
            <div className="font-group">
              <h4>Font Family</h4>
              <div className="font-options">
                {fontFamilies.map(font => (
                  <button
                    key={font}
                    className={`font-option ${visualSettings.fontFamily === font ? 'selected' : ''}`}
                    style={{ fontFamily: font }}
                    onClick={() => onUpdateSettings({ fontFamily: font })}
                  >
                    {font.split(',')[0]}
                  </button>
                ))}
              </div>
            </div>
            <div className="font-group">
              <h4>Font Size</h4>
              <div className="size-options">
                {fontSizes.map(size => (
                  <button
                    key={size}
                    className={`size-option ${visualSettings.fontSize === size ? 'selected' : ''}`}
                    onClick={() => onUpdateSettings({ fontSize: size })}
                  >
                    {size}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'stickers' && (
          <div className="stickers-section">
            <h4>Add Stickers</h4>
            <div className="sticker-grid">
              {stickerTypes.map(sticker => (
                <button
                  key={sticker}
                  className="sticker-option"
                  onClick={() => handleStickerAdd(sticker)}
                >
                  {sticker}
                </button>
              ))}
            </div>

            {visualSettings.stickers.length > 0 && (
              <div className="current-stickers">
                <h4>Current Stickers</h4>
                <div className="sticker-list">
                  {visualSettings.stickers.map(sticker => (
                    <div key={sticker.id} className="sticker-item">
                      <span className="sticker-preview">{sticker.type}</span>
                      <button
                        className="remove-sticker"
                        onClick={() => handleStickerRemove(sticker.id)}
                      >
                        ×
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default CustomizationPanel;
