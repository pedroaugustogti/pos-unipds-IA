import { Module } from '@nestjs/common';
import { CfpController } from './cfp.controller';
import { CfpService } from './cfp.service';

@Module({
  controllers: [CfpController],
  providers: [CfpService],
})
export class CfpModule {}
