import { Injectable } from '@nestjs/common';
import { SpeakerDTO } from '@cfp-platform/shared-types';
import { CreateSpeakerDto } from './create-speaker.dto';

@Injectable()
export class CfpService {
  private readonly submissions = new Map<string, SpeakerDTO>();

  create(dto: CreateSpeakerDto): SpeakerDTO {
    const submission: SpeakerDTO = { ...dto };
    this.submissions.set(submission.id, submission);
    return submission;
  }
}
