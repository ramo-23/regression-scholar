import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import type { Source } from '../../models';

@Component({
  selector: 'app-sources-list',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './sources-list.component.html',
  styleUrls: ['./sources-list.component.scss']
})
export class SourcesListComponent {
  @Input() public sources: Source[] = [];
}
