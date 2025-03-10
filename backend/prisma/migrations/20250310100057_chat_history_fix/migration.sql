/*
  Warnings:

  - You are about to drop the column `userEmail` on the `ChatHistory` table. All the data in the column will be lost.
  - Added the required column `userId` to the `ChatHistory` table without a default value. This is not possible if the table is not empty.

*/
-- DropIndex
DROP INDEX "ChatHistory_userEmail_idx";

-- AlterTable
ALTER TABLE "ChatHistory" DROP COLUMN "userEmail",
ADD COLUMN     "userId" TEXT NOT NULL;

-- CreateIndex
CREATE INDEX "ChatHistory_userId_idx" ON "ChatHistory"("userId");

-- AddForeignKey
ALTER TABLE "ChatHistory" ADD CONSTRAINT "ChatHistory_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;
