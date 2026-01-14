import { Component, Input, OnChanges, SimpleChanges, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';

@Component({
  selector: 'app-answer-card',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './answer-card.component.html',
  styleUrls: ['./answer-card.component.scss']
})
export class AnswerCardComponent implements OnChanges {
  @Input() public answer: string | null = null;
  @Input() public loading = false;

  constructor(private sanitizer: DomSanitizer, private cdr: ChangeDetectorRef) {}

  public safeHtml: SafeHtml | null = null;

  public paragraphs(): string[] {
    if (!this.answer) return [];
    return this.answer.split(/\n\n+/).map((p) => p.trim()).filter(Boolean);
  }

  public ngOnChanges(changes: SimpleChanges): void {
    if (!('answer' in changes)) return;
    if (!this.answer) {
      this.safeHtml = null;
      return;
    }

    const katex = (window as any).katex as any | undefined;
    const html = this.blockHtmlFromText(this.answer, katex);

    this.safeHtml = this.sanitizer.bypassSecurityTrustHtml(html);
    console.log('AnswerCard set safeHtml', { length: html.length });
    // ensure view updates immediately
    try { this.cdr.detectChanges(); } catch (e) { /* ignore */ }
  }

  private blockHtmlFromText(text: string, katex?: any): string {
    // normalize newlines
    const normalized = text.replace(/\r\n/g, '\n').replace(/\r/g, '\n');
    const blocks = normalized.split(/\n\n+/).map(b => b.trim()).filter(Boolean);

    const htmlBlocks = blocks.map(block => {
      const trimmed = block.trim();
      // if the block looks like a standalone title (e.g. "Sparsity and Variable Selection (Dimension Reduction)")
      if (this.isTitleLike(trimmed)) {
        return `<p><strong>${this.escapeHtml(trimmed)}</strong></p>`;
      }
      // heading like: Solution: or ### Solution
      const headingMatch = trimmed.match(/^#{1,6}\s*(.+)$/m);
      if (/^\s*Solution\s*[:\-]?/i.test(trimmed)) {
        const title = trimmed.replace(/^\s*Solution\s*[:\-]?\s*/i, '').trim() || 'Solution';
        return `<p><strong>${this.escapeHtml(title)}</strong></p>`;
      }
      if (headingMatch) {
        // render markdown headings as bold paragraphs (same font size)
        return `<p><strong>${this.escapeHtml(headingMatch[1].trim())}</strong></p>`;
      }

      // lists
      const lines = block.split(/\n/).map(l => l.trim());
      const isUnordered = lines.every(l => /^[-*+]\s+/.test(l));
      const isOrdered = lines.every(l => /^\d+\.\s+/.test(l));
      if (isUnordered) {
        const items = lines.map(l => l.replace(/^[-*+]\s+/, '')).map(item => {
          const inner = this.processInline(item, katex);
          return /<strong>/i.test(inner) ? `<li>${inner}</li>` : `<li><strong>${inner}</strong></li>`;
        }).join('');
        return `<ul>${items}</ul>`;
      }
      if (isOrdered) {
        const items = lines.map(l => l.replace(/^\d+\.\s+/, '')).map(item => {
          const inner = this.processInline(item, katex);
          return /<strong>/i.test(inner) ? `<li>${inner}</li>` : `<li><strong>${inner}</strong></li>`;
        }).join('');
        return `<ol>${items}</ol>`;
      }

      // default paragraph
      return `<p>${this.processInline(block, katex)}</p>`;
    });

    return htmlBlocks.join('');
  }

  private isTitleLike(block: string): boolean {
    // Consider short, title-cased or parenthesized lines as titles
    const plain = block.replace(/^#+\s*/, '').trim();
    const words = plain.split(/\s+/).filter(Boolean);
    if (words.length === 0) return false;
    if (words.length > 8) return false;
    // All-caps or contains parentheses
    if (/^[A-Z0-9 \-()\/:,&]+$/.test(plain) && plain.length < 80) return true;
    // Title case heuristic: most words start with uppercase letter
    const titleWords = words.filter(w => /^[A-Z][a-z0-9\(\[]/.test(w)).length;
    if (titleWords >= Math.max(1, Math.floor(words.length * 0.6))) return true;
    // explicit patterns like 'Sparsity and Variable Selection' (has capitalized words)
    return false;
  }

  private processInline(text: string, katex?: any): string {
    // Pre-wrap common math patterns (e.g., X^T X) if not already in $...$
    // only when no $ present to avoid double-wrapping
    if (!/\$/.test(text)) {
      text = text.replace(/\bX\^T\s*X\b/g, '$$X^T X$$');
      text = text.replace(/\bX\^T\s*X\b/g, '$X^T X$');
    }

    if (!katex) {
      // convert **bold** markers to <strong> and highlight keywords without double-wrapping
      const html = this.parseBoldToHtml(text);
      return this.highlightKeywordsInHtml(html);
    }

    const parts: string[] = [];
    const regex = /(\$\$([\s\S]*?)\$\$|\$([^$][\s\S]*?)\$)/g;
    let lastIndex = 0;
    let m: RegExpExecArray | null;
    while ((m = regex.exec(text)) !== null) {
      const idx = m.index;
      if (idx > lastIndex) {
        const plain = text.slice(lastIndex, idx);
        parts.push(this.highlightKeywordsInHtml(this.parseBoldToHtml(plain)));
      }
      const display = m[2];
      const inline = m[3];
      if (display !== undefined) {
        try {
          parts.push(katex.renderToString(display, { throwOnError: false, displayMode: true }));
        } catch (e) {
          parts.push(this.escapeHtml(m[0]));
        }
      } else if (inline !== undefined) {
        try {
          parts.push(katex.renderToString(inline, { throwOnError: false, displayMode: false }));
        } catch (e) {
          parts.push(this.escapeHtml(m[0]));
        }
      }
      lastIndex = regex.lastIndex;
    }
    if (lastIndex < text.length) parts.push(this.highlightKeywordsInHtml(this.parseBoldToHtml(text.slice(lastIndex))));
    return parts.join('');
  }

  private parseBoldToHtml(text: string): string {
    const regex = /\*\*(.*?)\*\*/gs;
    let out = '';
    let last = 0;
    let m: RegExpExecArray | null;
    while ((m = regex.exec(text)) !== null) {
      out += this.escapeHtml(text.slice(last, m.index));
      out += `<strong>${this.escapeHtml(m[1])}</strong>`;
      last = regex.lastIndex;
    }
    out += this.escapeHtml(text.slice(last));
    return out;
  }

  private highlightKeywordsInHtml(html: string): string {
    const keywords = ['Ridge', 'L2', 'regularization', 'regularize', 'PCA', 'SVD', 'pseudoinverse', 'VIF', 'condition number', 'ill-conditioned', 'multicollinearity'];
    const pattern = new RegExp('\\b(' + keywords.map(k => k.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&')).join('|') + ')\\b', 'gi');

    const tokens = html.split(/(<[^>]+>)/g);
    let inStrong = false;
    for (let i = 0; i < tokens.length; i++) {
      const t = tokens[i];
      if (!t) continue;
      if (/^<\s*strong\b/i.test(t)) { inStrong = true; continue; }
      if (/^<\s*\/\s*strong\b/i.test(t)) { inStrong = false; continue; }
      if (t.startsWith('<')) continue; // other tags
      if (!inStrong) {
        tokens[i] = t.replace(pattern, '<strong>$1</strong>');
      }
    }
    return tokens.join('');
  }

  private highlightKeywords(escaped: string): string {
    // wrap key terms with <strong> for emphasis
    const keywords = ['Ridge', 'L2', 'regularization', 'regularize', 'PCA', 'SVD', 'pseudoinverse', 'VIF', 'condition number', 'ill-conditioned', 'multicollinearity'];
    const pattern = new RegExp('\\\b(' + keywords.map(k => k.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&')).join('|') + ')\\b', 'gi');
    return escaped.replace(pattern, '<strong>$1</strong>');
  }

  private escapeHtml(text: string): string {
    return text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }
}
