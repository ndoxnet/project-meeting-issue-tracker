// Concept by MrHan (08974747477)
import { describe, expect, it } from 'vitest';
import { render, screen, within } from '@testing-library/react';
import { DistributionBars } from './DistributionBars';
import { TrendTable } from './TrendTable';

describe('DistributionBars', () => {
  it('exposes each label and its numeric count as text (not bar length alone)', () => {
    render(
      <DistributionBars
        data={[
          { label: 'Engineering', count: 3 },
          { label: 'Procurement', count: 1 },
        ]}
      />,
    );
    expect(screen.getByText('Engineering')).toBeInTheDocument();
    expect(screen.getByText('3')).toBeInTheDocument();
    expect(screen.getByText('Procurement')).toBeInTheDocument();
  });
});

describe('TrendTable', () => {
  it('renders an accessible table with month rows and numeric values', () => {
    render(
      <TrendTable
        data={[
          { month: '2026-06', opened: 4, closed: 2 },
          { month: '2026-07', opened: 5, closed: 3 },
        ]}
      />,
    );
    expect(screen.getByRole('columnheader', { name: 'Opened' })).toBeInTheDocument();
    expect(screen.getByRole('columnheader', { name: 'Closed' })).toBeInTheDocument();
    const june = screen.getByRole('row', { name: /2026-06/ });
    expect(within(june).getByText('4')).toBeInTheDocument();
    expect(within(june).getByText('2')).toBeInTheDocument();
  });
});
