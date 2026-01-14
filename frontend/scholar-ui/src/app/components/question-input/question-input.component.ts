import { Component, EventEmitter, Input, Output, OnChanges, SimpleChanges } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-question-input',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './question-input.component.html',
  styleUrls: ['./question-input.component.scss']
})
export class QuestionInputComponent implements OnChanges {
  @Input() public initial = '';
  @Input() public loading = false;
  @Output() public submitQuestion = new EventEmitter<string>();

  public text = '';

  public ngOnChanges(changes: SimpleChanges): void {
    if (changes['initial'] && typeof this.initial === 'string') {
      this.text = this.initial;
    }
  }

  public submit(): void {
    const q = (this.text || '').trim();
    if (!q) return;
    this.submitQuestion.emit(q);
  }

  public onEnter(event: Event): void {
    // KeyboardEvent typing can be widened in some Angular template checks;
    // cast here to avoid template type mismatch diagnostics.
    (event as KeyboardEvent).preventDefault?.();
    this.submit();
  }
}
