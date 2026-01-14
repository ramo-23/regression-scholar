import { Component, ChangeDetectorRef } from '@angular/core';
import { finalize } from 'rxjs';
import { CommonModule } from '@angular/common';

import { HeaderComponent } from './components/header/header.component';
import { QuestionInputComponent } from './components/question-input/question-input.component';
import { AnswerCardComponent } from './components/answer-card/answer-card.component';
import { SourcesListComponent } from './components/sources-list/sources-list.component';
import { SuggestedQuestionsComponent } from './components/suggested-questions/suggested-questions.component';
import { ScholarService } from './services/scholar.service';
import type { Source } from './models';
import { RouterOutlet } from "@angular/router";

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, HeaderComponent, QuestionInputComponent, AnswerCardComponent, SourcesListComponent, SuggestedQuestionsComponent, RouterOutlet],
  templateUrl: './app.html',
  styleUrls: ['./app.scss']
})
export class App {
  public question = '';
  public answer: string | null = null;
  public sources: Source[] = [];
  public loading = false;
  public error: string | null = null;
  public currentYear = new Date().getFullYear();

  constructor(private readonly scholar: ScholarService, private cdr: ChangeDetectorRef) {}

  // In development, populate a sample answer so the AnswerCard shows formatted output on localhost
  // This is gated to localhost to avoid affecting production behavior.
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  private _devInjectSample(): void {
    try {
      const host = (typeof window !== 'undefined' && (window as any).location && (window as any).location.hostname) ? (window as any).location.hostname : '';
      if (!/localhost|127\.0\.0\.1/.test(host)) return;
      const sample = `### Definition and Mathematical Formulation

$$\\hat{\\beta}_{\\lambda} = (X^{T}X + \\lambda I_p)^{-1} X^{T} y$$

- **X** is the design matrix.
- **y** is the response vector.
- **\\lambda** is the ridge parameter, a positive scalar (\\lambda>0).
- **I_p** is the p\\times p identity matrix.

### Key Properties and Characteristics

1. **Ridge (L2) regularization reduces multicollinearity by adding \\lambda I_p to X^{T}X.**
2. **Stabilizes inversion of ill-conditioned X^{T}X (reduces condition number).**
3. **Bias–variance tradeoff: small bias for substantially lower variance.**
4. **Can be interpreted via SVD/PCA — shrinks components with small singular values.**
5. **Alternatives: LASSO, PCA, pseudoinverse, VIF checks.**`;
      this.answer = sample;
      this.loading = false;
      console.log('Dev sample answer injected');
    } catch (e) {
      /* ignore */
    }
  }


  public onAsk(question: string): void {
    this.error = null;
    this.answer = null;
    this.sources = [];
    this.loading = true;
    this.scholar.ask(question).pipe(
      finalize(() => {
        this.loading = false;
        try { this.cdr.detectChanges(); } catch (e) { /* ignore */ }
        console.log('loading finalized (set to false)');
      })
    ).subscribe({
      next: (res) => {
        console.log('ask response', res);
        this.answer = res.answer;
        // backend may return sources with keys like `paper_title` and `link`
        const raw = (res.sources ?? []) as Array<any>;
        this.sources = raw.map((s) => ({
          title: s.paper_title ?? s.title ?? '',
          authors: s.authors ?? s.author ?? '',
          section: s.section ?? '',
          arxiv_url: s.link ?? s.arxiv_url ?? '',
        }));
      },
      error: (err) => {
        this.error = (err && err.message) ? err.message : 'Request failed';
      }
    });
  }

  public onSuggestion(question: string): void {
    this.question = question;
    // auto-submit
    this.onAsk(question);
  }
}
