import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { SpeakerDTO } from '@cfp-platform/shared-types';

@Injectable({ providedIn: 'root' })
export class CfpService {
  private readonly http = inject(HttpClient);

  submit(speaker: SpeakerDTO): Observable<SpeakerDTO> {
    return this.http.post<SpeakerDTO>('/api/cfp', speaker);
  }
}
