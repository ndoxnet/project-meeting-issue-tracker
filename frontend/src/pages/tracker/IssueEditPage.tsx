// Concept by MrHan (08974747477)
import { useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useNavigate, useParams } from 'react-router-dom';
import { usePageTitle } from '@/hooks/usePageTitle';
import { PageHeader } from '@/components/layout/PageHeader';
import { DataState } from '@/components/feedback/DataState';
import { Field, Select, TextArea, TextInput } from '@/components/ui/Field';
import { Button } from '@/components/ui/Button';
import { InlineError } from '@/components/feedback/InlineError';
import { useIssue, useUpdateIssue } from '@/api/issues';
import { useCategories, useResponsibleParties } from '@/api/masterdata';
import { ISSUE_PRIORITIES, type IssueMetadataUpdate } from '@/api/types';

const schema = z.object({
  title: z.string().min(1, 'Title is required').max(300),
  description: z.string().min(1, 'Description is required'),
  category_id: z.string().min(1),
  responsible_party_id: z.string(),
  priority: z.enum(['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']),
  pic_name: z.string(),
  due_date: z.string(),
  next_action: z.string(),
  change_reason: z.string(),
});
type FormValues = z.infer<typeof schema>;

const norm = (v: string | null | undefined) => (v && v.length ? v : null);

export function IssueEditPage() {
  usePageTitle('Edit issue');
  const { issueId = '' } = useParams();
  const navigate = useNavigate();
  const issue = useIssue(issueId);
  const update = useUpdateIssue(issueId);
  const categories = useCategories();
  const parties = useResponsibleParties();

  const {
    register,
    handleSubmit,
    reset,
    setError,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({ resolver: zodResolver(schema) });

  // Populate the form from the loaded issue.
  useEffect(() => {
    const d = issue.data;
    if (!d) return;
    reset({
      title: d.title,
      description: d.description,
      category_id: d.category_id,
      responsible_party_id: d.responsible_party_id ?? '',
      priority: d.priority,
      pic_name: d.pic_name ?? '',
      due_date: d.due_date ?? '',
      next_action: d.next_action ?? '',
      change_reason: '',
    });
  }, [issue.data, reset]);

  function onSubmit(v: FormValues) {
    const d = issue.data;
    if (!d) return;

    const picChanged = norm(v.pic_name) !== norm(d.pic_name);
    const dueChanged = norm(v.due_date) !== norm(d.due_date);
    if ((picChanged || dueChanged) && !v.change_reason.trim()) {
      setError('change_reason', {
        message: 'A change reason is required when changing PIC or due date.',
      });
      return;
    }

    // Send only changed fields (the backend treats any sent PIC/due as a change).
    const body: IssueMetadataUpdate = {};
    if (v.title !== d.title) body.title = v.title;
    if (v.description !== d.description) body.description = v.description;
    if (v.category_id !== d.category_id) body.category_id = v.category_id;
    if (norm(v.responsible_party_id) !== norm(d.responsible_party_id))
      body.responsible_party_id = norm(v.responsible_party_id);
    if (v.priority !== d.priority) body.priority = v.priority;
    if (norm(v.next_action) !== norm(d.next_action)) body.next_action = norm(v.next_action);
    if (picChanged) body.pic_name = norm(v.pic_name);
    if (dueChanged) body.due_date = norm(v.due_date);
    if (picChanged || dueChanged) body.change_reason = v.change_reason.trim();

    if (Object.keys(body).length === 0) {
      navigate(`/app/issues/${issueId}`);
      return;
    }
    update.mutate(body, { onSuccess: () => navigate(`/app/issues/${issueId}`) });
  }

  return (
    <section>
      <PageHeader title="Edit Issue" backTo={`/app/issues/${issueId}`} backLabel="Back to issue" />
      <DataState isLoading={issue.isLoading} error={issue.error} loadingLabel="Loading issue…">
        {issue.data && (
          <form className="max-w-2xl space-y-4" onSubmit={handleSubmit(onSubmit)} noValidate>
            <Field label="Title" htmlFor="e-title" required error={errors.title?.message}>
              <TextInput id="e-title" {...register('title')} />
            </Field>
            <Field
              label="Description"
              htmlFor="e-description"
              required
              error={errors.description?.message}
            >
              <TextArea id="e-description" {...register('description')} />
            </Field>
            <div className="grid gap-4 sm:grid-cols-2">
              <Field label="Category" htmlFor="e-category">
                <Select id="e-category" {...register('category_id')}>
                  {categories.data?.items.map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.name}
                    </option>
                  ))}
                </Select>
              </Field>
              <Field label="Responsible party" htmlFor="e-rp">
                <Select id="e-rp" {...register('responsible_party_id')}>
                  <option value="">—</option>
                  {parties.data?.items.map((p) => (
                    <option key={p.id} value={p.id}>
                      {p.name}
                    </option>
                  ))}
                </Select>
              </Field>
              <Field label="Priority" htmlFor="e-priority">
                <Select id="e-priority" {...register('priority')}>
                  {ISSUE_PRIORITIES.map((p) => (
                    <option key={p} value={p}>
                      {p}
                    </option>
                  ))}
                </Select>
              </Field>
              <Field label="PIC name" htmlFor="e-pic">
                <TextInput id="e-pic" {...register('pic_name')} />
              </Field>
              <Field label="Due date" htmlFor="e-due">
                <TextInput id="e-due" type="date" {...register('due_date')} />
              </Field>
              <Field label="Next action" htmlFor="e-next">
                <TextInput id="e-next" {...register('next_action')} />
              </Field>
            </div>
            <Field
              label="Change reason"
              htmlFor="e-reason"
              hint="Required when changing PIC or due date."
              error={errors.change_reason?.message}
            >
              <TextInput id="e-reason" {...register('change_reason')} />
            </Field>

            {update.error != null && <InlineError error={update.error} />}

            <div className="flex gap-2">
              <Button type="submit" loading={isSubmitting || update.isPending}>
                Save changes
              </Button>
              <Button
                type="button"
                variant="ghost"
                onClick={() => navigate(`/app/issues/${issueId}`)}
              >
                Cancel
              </Button>
            </div>
          </form>
        )}
      </DataState>
    </section>
  );
}
