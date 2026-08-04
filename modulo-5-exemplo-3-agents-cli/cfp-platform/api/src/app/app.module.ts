import { Module } from '@nestjs/common';
import { AppController } from './app.controller';
import { AppService } from './app.service';
import { CfpModule } from './cfp/cfp.module';

@Module({
  imports: [CfpModule],
  controllers: [AppController],
  providers: [AppService],
})
export class AppModule {}
