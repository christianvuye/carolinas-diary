import { render } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';

import App from './App';

test('renders app component', () => {
  render(
    <MemoryRouter>
      <App />
    </MemoryRouter>
  );
  // Just test that the app renders without crashing
  expect(document.body).toBeInTheDocument();
});
