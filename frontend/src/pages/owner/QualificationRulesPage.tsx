import React, { useEffect, useState } from 'react';
import { ShieldCheck, Plus, Trash2, Edit, Check, X } from 'lucide-react';
import { qualificationService } from '../../services/qualification';
import { QualificationRule } from '../../types';
import { Button } from '../../components/ui/Button';
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/Card';
import { Dialog } from '../../components/ui/Dialog';
import { LoadingSpinner } from '../../components/ui/LoadingState';
import { Badge } from '../../components/ui/Badge';

export const QualificationRulesPage: React.FC = () => {
  const [rules, setRules] = useState<QualificationRule[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const [newRule, setNewRule] = useState({
    name: '',
    field: 'investment_capacity',
    operator: 'gte',
    value: '2500000',
    score: 20,
    priority: 1,
    active: true,
  });

  const loadRules = async () => {
    setLoading(true);
    try {
      const data = await qualificationService.getRules();
      setRules(data);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadRules();
  }, []);

  const handleCreateRule = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await qualificationService.createRule(newRule as any);
      setIsModalOpen(false);
      loadRules();
    } catch (err: any) {
      alert('Error creating rule.');
    }
  };

  const handleToggleRuleActive = async (rule: QualificationRule) => {
    try {
      await qualificationService.updateRule(rule.id, { active: !rule.active });
      loadRules();
    } catch (err: any) {
      alert('Error toggling rule active status.');
    }
  };

  const handleDeleteRule = async (id: number) => {
    if (!confirm('Are you sure you want to delete this qualification rule?')) return;
    try {
      await qualificationService.deleteRule(id);
      loadRules();
    } catch (err: any) {
      alert('Error deleting rule.');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h2 className="text-2xl font-bold text-slate-900 tracking-tight">Qualification Engine Configurator</h2>
          <p className="text-sm text-slate-500">Configure brand qualification scoring rules. Django evaluates these rules server-side for every lead.</p>
        </div>
        <Button onClick={() => setIsModalOpen(true)} icon={<Plus className="h-4 w-4" />}>
          Add Scoring Rule
        </Button>
      </div>

      <Card>
        <CardContent className="p-0">
          {loading ? (
            <LoadingSpinner text="Loading Qualification Rules..." />
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm text-slate-600">
                <thead className="bg-slate-50 border-b border-slate-100 text-xs font-semibold text-slate-500 uppercase">
                  <tr>
                    <th className="px-6 py-3">Priority</th>
                    <th className="px-6 py-3">Rule Name</th>
                    <th className="px-6 py-3">Evaluated Field</th>
                    <th className="px-6 py-3">Operator</th>
                    <th className="px-6 py-3">Target Value</th>
                    <th className="px-6 py-3">Score (+/-)</th>
                    <th className="px-6 py-3">Status</th>
                    <th className="px-6 py-3 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {rules.map((rule) => (
                    <tr key={rule.id} className="hover:bg-slate-50/50">
                      <td className="px-6 py-4 font-mono font-bold text-slate-900">{rule.priority}</td>
                      <td className="px-6 py-4 font-semibold text-slate-900">{rule.name}</td>
                      <td className="px-6 py-4 font-mono text-xs text-sky-700 bg-sky-50 px-2 py-0.5 rounded w-fit">{rule.field}</td>
                      <td className="px-6 py-4 text-xs font-medium">{rule.operator_display || rule.operator}</td>
                      <td className="px-6 py-4 font-mono text-xs text-slate-800">{rule.value || 'N/A'}</td>
                      <td className="px-6 py-4 font-bold text-emerald-700">+{rule.score}</td>
                      <td className="px-6 py-4">
                        {rule.active ? (
                          <Badge variant="qualified">Active</Badge>
                        ) : (
                          <Badge variant="outline">Disabled</Badge>
                        )}
                      </td>
                      <td className="px-6 py-4 text-right space-x-2">
                        <button
                          onClick={() => handleToggleRuleActive(rule)}
                          className="p-1.5 text-slate-500 hover:text-slate-900 hover:bg-slate-100 rounded-md"
                          title="Toggle Active"
                        >
                          {rule.active ? <X className="h-4 w-4 text-amber-600" /> : <Check className="h-4 w-4 text-emerald-600" />}
                        </button>
                        <button
                          onClick={() => handleDeleteRule(rule.id)}
                          className="p-1.5 text-slate-500 hover:text-rose-600 hover:bg-rose-50 rounded-md"
                          title="Delete Rule"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Add Rule Dialog */}
      <Dialog isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title="Create Qualification Rule">
        <form onSubmit={handleCreateRule} className="space-y-4 text-xs">
          <div>
            <label className="font-semibold text-slate-700 block mb-1">Rule Name</label>
            <input
              type="text"
              required
              placeholder="e.g. Investment >= ₹25L"
              value={newRule.name}
              onChange={(e) => setNewRule({ ...newRule, name: e.target.value })}
              className="w-full px-3 py-2 border border-slate-200 rounded-lg"
            />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="font-semibold text-slate-700 block mb-1">Target Lead Field</label>
              <select
                value={newRule.field}
                onChange={(e) => setNewRule({ ...newRule, field: e.target.value })}
                className="w-full px-3 py-2 border border-slate-200 rounded-lg"
              >
                <option value="investment_capacity">investment_capacity</option>
                <option value="preferred_location">preferred_location</option>
                <option value="property_available">property_available</option>
                <option value="business_experience">business_experience</option>
                <option value="expected_start">expected_start</option>
              </select>
            </div>
            <div>
              <label className="font-semibold text-slate-700 block mb-1">Operator</label>
              <select
                value={newRule.operator}
                onChange={(e) => setNewRule({ ...newRule, operator: e.target.value as any })}
                className="w-full px-3 py-2 border border-slate-200 rounded-lg"
              >
                <option value="gte">&gt;= (Greater than or equal)</option>
                <option value="lte">&lt;= (Less than or equal)</option>
                <option value="eq">= (Equal)</option>

                <option value="contains">Contains</option>
                <option value="is_true">Is True</option>
                <option value="is_false">Is False</option>
              </select>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="font-semibold text-slate-700 block mb-1">Value (if applicable)</label>
              <input
                type="text"
                value={newRule.value}
                onChange={(e) => setNewRule({ ...newRule, value: e.target.value })}
                className="w-full px-3 py-2 border border-slate-200 rounded-lg"
              />
            </div>
            <div>
              <label className="font-semibold text-slate-700 block mb-1">Score (+ Points)</label>
              <input
                type="number"
                required
                value={newRule.score}
                onChange={(e) => setNewRule({ ...newRule, score: parseInt(e.target.value) || 0 })}
                className="w-full px-3 py-2 border border-slate-200 rounded-lg"
              />
            </div>
          </div>
          <div className="flex justify-end gap-2 pt-4">
            <Button type="button" variant="outline" onClick={() => setIsModalOpen(false)}>Cancel</Button>
            <Button type="submit">Create Scoring Rule</Button>
          </div>
        </form>
      </Dialog>
    </div>
  );
};
