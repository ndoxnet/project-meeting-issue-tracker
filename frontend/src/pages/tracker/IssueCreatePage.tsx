// Concept by MrHan (08974747477)
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useNavigate } from 'react-router-dom';
import { usePageTitle } from '@/hooks/usePageTitle';
import { PageHeader } from '@/components/layout/PageHeader';
import { Field, Select, TextArea, TextInput } from '@/components/ui/Field';
import { Button } from '@/components/ui/Button';
import { InlineError } from '@/components/feedback/InlineError';
import { useCreateIssue } from '@/api/issues';
import { useCategories, useResponsibleParties } from '@/api/masterdata';
import { useOccurrences } from '@/api/meetings';
import { ISSUE_PRIORITIES, type IssueCreate } from '@/api/types';
import { formatDate } from '@/lib/dates';

const schema = z
  .object({
    title: z.string().min(1, 'Title is required').max(300),
    description: z.string().min(1, 'Description is required'),
    category_id: z.string().min(1, 'Select a category'),
    responsible_party_id: z.string().optional(),
    priority: z.enum(['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']),
    raised_date: z.string().min(1, 'Raised date is required'),
    due_date: z.string().optional(),
    raised_in_meeting_occurrence_id: z.string().optional(),
    pic_name: z.string().optional(),
    next_action: z.string().optional(),
  })
  .refine((v) => !v.due_date || v.due_date >= v.raised_date, {
    message: 'Due date cannot be before the raised date',
    path: ['due_date'],
  });

type FormValues = z.infer<typeof schema>;

export function IssueCreatePage() {
  usePageTitle('New issue');
  const navigate = useNavigate();
  const categories = useCategories();
  const parties = useResponsibleParties();
  const occurrences = useOccurrences({ page: 1, page_size: 200 });
  const create = useCreateIssue();

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { priority: 'MEDIUM', raised_date: new Date().toISOString().slice(0, 10) },
  });

  function onSubmit(v: FormValues) {
    const body: IssueCreate = {
      title: v.title,
      description: v.description,
      category_id: v.category_id,
      responsible_party_id: v.responsible_party_id || null,
      priority: v.priority,
      raised_date: v.raised_date,
      due_date: v.due_date || null,
      raised_in_meeting_occurrence_id: v.raised_in_meeting_occurrence_id || null,
      pic_name: v.pic_name || null,
      next_action: v.next_action || null,
      confirm_possible_duplicate: false,
    };
    create.mutate(body, {
      onSuccess: (res) => navigate(`/app/issues/${res.issue.id}`),
    });
  }

  return (
    <section>
      <PageHeader title="New Issue" backTo="/app/issues" backLabel="Back to issues" />
      <form className="max-w-2xl space-y-4" onSubmit={handleSubmit(onSubmit)} noValidate>
        <Field label="Title" htmlFor="title" required error={errors.title?.message}>
          <TextInput id="title" {...register('title')} />
        </Field>
        <Field label="Description" htmlFor="description" required error={errors.description?.message}>
          <TextArea id="description" {...register('description')} />
        </Field>
        <div className="grid gap-4 sm:grid-cols-2">
          <Field label="Category" htmlFor="category_id" required error={errors.category_id?.message}>
            <Select id="category_id" {...register('category_id')} defaultValue="">
              <option value="" disabled>
                Select…
              </option>
              {categories.data?.items.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                </option>
              ))}
            </Select>
          </Field>
          <Field label="Responsible party" htmlFor="responsible_party_id">
            <Select id="responsible_party_id" {...register('responsible_party_id')} defaultValue="">
              <option value="">—</option>
              {parties.data?.items.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name}
                </option>
              ))}
            </Select>
          </Field>
          <Field label="Priority" htmlFor="priority" required>
            <Select id="priority" {...register('priority')}>
              {ISSUE_PRIORITIES.map((p) => (
                <option key={p} value={p}>
                  {p}
                </option>
              ))}
            </Select>
          </Field>
          <Field label="Raised in meeting" htmlFor="occ">
            <Select id="occ" {...register('raised_in_meeting_occurrence_id')} defaultValue="">
              <option value="">—</option>
              {occurrences.data?.items.map((o) => (
                <option key={o.id} value={o.id}>
                  {formatDate(o.meeting_date)} {o.meeting_number ?? ''}
                </option>
              ))}
            </Select>
          </Field>
          <Field label="Raised date" htmlFor="raised_date" required error={errors.raised_date?.message}>
            <TextInput id="raised_date" type="date" {...register('raised_date')} />
          </Field>
          <Field label="Due date" htmlFor="due_date" error={errors.due_date?.message}>
            <TextInput id="due_date" type="date" {...register('due_date')} />
          </Field>
          <Field label="PIC name" htmlFor="pic_name">
            <TextInput id="pic_name" {...register('pic_name')} />
          </Field>
          <Field label="Next action" htmlFor="next_action">
            <TextInput id="next_action" {...register('next_action')} />
          </Field>
        </div>

        {create.error != null && <InlineError error={create.error} />}

        <div className="flex gap-2">
          <Button type="submit" loading={isSubmitting || create.isPending}>
            Create issue
          </Button>
          <Button type="button" variant="ghost" onClick={() => navigate('/app/issues')}>
            Cancel
          </Button>
        </div>
      </form>
    </section>
  );
}
