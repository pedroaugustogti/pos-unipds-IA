import { Body, Controller, HttpCode, Post } from '@nestjs/common';
import { SpeakerDTO } from '@cfp-platform/shared-types';
import { CfpService } from './cfp.service';
import { CreateSpeakerDto } from './create-speaker.dto';

@Controller()
export class CfpController {
  constructor(private readonly cfpService: CfpService) {}

  @Post('cfp')
  @HttpCode(201)
  create(@Body() dto: CreateSpeakerDto): SpeakerDTO {
    return this.cfpService.create(dto);
  }
}
