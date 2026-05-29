# YGO JUDGE LAB - EVALUATION DATASET (THEORETICAL RAG TESTS)

Bộ câu hỏi này được thiết kế thuần túy dựa trên cơ chế hệ thống, cấu trúc văn bản (PSCT), logic từ nối (Conjunctions) và phân bậc chuỗi (SEGOC) để đánh giá năng lực suy luận của AI Agent mà không phụ thuộc vào dữ liệu lá bài cụ thể.

---

## Câu hỏi 1: Kiểm tra tư duy hệ thống SEGOC (Phân bậc Chain)

### Tình huống
Một chuỗi các sự kiện xảy ra trong trận đấu khiến cho cùng một lúc có 4 hiệu ứng sau đây đủ điều kiện để tuyên bố kích hoạt:
1. **Hiệu ứng A:** Hiệu ứng Tự nguyện (Optional Effect) của Đối thủ (Opponent).
2. **Hiệu ứng B:** Hiệu ứng Bắt buộc (Mandatory Effect) của Người chơi có lượt (Turn Player).
3. **Hiệu ứng C:** Hiệu ứng Tự nguyện (Optional Effect) của Người chơi có lượt (Turn Player).
4. **Hiệu ứng D:** Hiệu ứng Bắt buộc (Mandatory Effect) của Đối thủ (Opponent).

### Câu hỏi
1. Dựa vào quy tắc SEGOC (Simultaneous Effects Go On Chain), hãy sắp xếp thứ tự bắt buộc của các hiệu ứng này từ Chain Link 1 đến Chain Link 4.
2. Người chơi có quyền tự do hoán đổi vị trí (Chain Blocking) của các hiệu ứng nào cho nhau trong tình huống này không? Vì sao?

### Câu trả lời kỳ vọng (Expected Output)
- **Thứ tự Chain Link bắt buộc:** - **Chain Link 1:** Hiệu ứng B (Bắt buộc của Turn Player - Category 1).
  - **Chain Link 2:** Hiệu ứng D (Bắt buộc của Opponent - Category 2).
  - **Chain Link 3:** Hiệu ứng C (Tự nguyện của Turn Player - Category 3).
  - **Chain Link 4:** Hiệu ứng A (Tự nguyện của Opponent - Category 4).
- **Quyết định về quyền hoán đổi:** Người chơi **KHÔNG** có quyền hoán đổi vị trí của bất kỳ hiệu ứng nào cho nhau. Quy tắc xếp tầng giữa 4 nhóm Category của SEGOC là tuyệt đối cố định. Người chơi chỉ có quyền tự do sắp xếp thứ tự nếu có từ 2 hiệu ứng trở lên cùng thuộc về một nhóm Category (ví dụ: cùng là Category 3).

---

## Câu hỏi 2: Kiểm tra khả năng bóc tách cấu trúc câu PSCT (Cost vs Effect)

### Tình huống
Một hiệu ứng của một lá bài khi kích hoạt được viết chính xác theo cấu trúc PSCT chuẩn như sau:
*"You can banish 1 card from your hand; target 1 face-up card on the field; destroy it."*

### Câu hỏi
Nếu hiệu ứng này bị một lá bài Counter Trap của đối thủ xích vào (Chain) để **Phủ nhận hoàn toàn sự kích hoạt (Negate the activation)**, hãy đưa ra phán quyết cho hai điểm sau:
1. Lá bài đã bị trục xuất ở bước đầu (`banish 1 card from your hand`) có được hoàn trả lại cho người chơi hay không? Vì sao?
2. Mục tiêu đã được chọn ở bước hai (`target 1 face-up card`) có được phép thay đổi sang một mục tiêu hợp lệ khác trên sân khi phân giải không? Vì sao?

### Câu trả lời kỳ vọng (Expected Output)
1. **KHÔNG được trả lại.** Hành động `banish 1 card from your hand` nằm trước dấu chấm phẩy (`;`) đầu tiên, đóng vai trò là **Cost (Chi phí kích hoạt)**. Luật PSCT quy định Cost phải được trả ngay lập tức tại thời điểm tuyên bố kích hoạt. Cho dù hiệu ứng sau đó bị phủ nhận hoàn toàn (Negate), tài nguyên dùng để trả Cost không bao giờ được hoàn lại.
2. **KHÔNG được thay đổi.** Hành động `target 1 face-up card` nằm trước dấu chấm phẩy (`;`) thứ hai, đây là hành động **Chỉ định mục tiêu lúc kích hoạt (Targeting at activation)**. Việc chọn mục tiêu diễn ra ở thời điểm mở Chain Link chứ không phải lúc phân giải (Resolution). Một khi Chain Link đã khóa, mục tiêu không thể thay đổi hoặc chọn lại, bất kể hiệu ứng sau đó có bị can thiệp hay phủ nhận.

---

## Câu hỏi 3: Kiểm tra logic toán học của từ nối "And If You Do" vs "Then"

### Tình huống
Xét hai lá bài có cấu trúc hiệu ứng như sau:
- **Lá bài A:** *"Do Hành động X, and if you do, do Hành động Y."*
- **Lá bài B:** *"Do Hành động X, then do Hành động Y."*

Trong quá trình phân giải hiệu ứng của cả hai lá bài, do một điều kiện bất khả kháng từ môi trường trận đấu, **Hành động X bị thất bại và không thể thực hiện thành công**.

### Câu hỏi
1. Đối với lá bài A, hành động Y có được tiếp tục thực hiện không? Trạng thái thời gian (Timing) của hành động Y (nếu xảy ra) được tính là đồng thời hay tuần tự sau hành động X?
2. Đối với lá bài B, hành động Y có được tiếp tục thực hiện không? Sự khác biệt cốt lõi về mặt mốc thời gian (Timing Application) giữa từ nối của lá A và lá B là gì?

### Câu trả lời kỳ vọng (Expected Output)
1. **Đối với lá bài A:** Hành động Y **KHÔNG** được thực hiện. Cấu trúc *"A, and if you do, B"* quy định hành động X là điều kiện tiên quyết nghiêm ngặt để có hành động Y. Về mặt mốc thời gian, cấu trúc này coi hành động X và hành động Y xảy ra **đồng thời (Simultaneously)**.
2. **Đối với lá bài B:** Hành động Y **KHÔNG** được thực hiện. Cấu trúc *"A, then B"* cũng yêu cầu hành động X phải thành công.
3. **Sự khác biệt cốt lõi về Timing:** Với cấu trúc của lá A ("And if you do"), hai hành động xảy ra cùng lúc, không làm mất thời điểm kích hoạt của các thẻ bài khác. Với cấu trúc của lá B ("Then"), hành động X xảy ra **trước**, hành động Y xảy ra **sau** (tuần tự). Điều này khiến hành động X bị đè dòng thời gian bởi hành động Y, có thể làm cho các hiệu ứng dạng *"When... you can"* phản ứng với hành động X bị **Lỡ thời điểm (Miss Timing)**.

---

## Câu hỏi 4: Kiểm tra sự xung đột giữa "And Also" và Loại bài bám sân

### Tình huống
Một lá bài thuộc loại **Ma pháp liên tục (Continuous Spell)** có văn bản hiệu ứng kích hoạt như sau:
*"Draw 1 card, and also after that, destroy 1 card you control."*

Người chơi lật ngửa lá bài này để tuyên bố kích hoạt hiệu ứng. Đối thủ lập tức phản công bằng cách Chain một lá bài khác để **Phá hủy (Destroy)** lá bài Continuous Spell này ngay trên Chain Link.

### Câu hỏi
Khi Chain Link này được phân giải (Resolve), người chơi có được thực hiện hành động rút 1 lá bài (`Draw 1 card`) và có phải thực hiện hành động phá hủy bài của mình (`destroy 1 card you control`) nữa không? Hãy giải thích dựa trên quy tắc tối cao của loại bài này.

### Câu trả lời kỳ vọng (Expected Output)
- **Phán quyết:** **KHÔNG LÀM GÌ CẢ** (Toàn bộ hiệu ứng phân giải thất bại hoàn toàn / Resolve without effect).
- **Giải thích:** Mặc dù từ nối *"And also"* về mặt văn bản quy định hai hành động (rút bài và phá hủy bài) hoàn toàn độc lập về mặt nhân quả (hành động trước lỗi thì hành động sau vẫn chạy). Tuy nhiên, lá bài này thuộc loại **Continuous Spell**. Luật tối cao của Yu-Gi-Oh! (The Golden Rule / Field Presence Rule) quy định các loại bài Continuous Spell/Trap, Field Spell, và Equip Spell bắt buộc phải **hiện diện ngửa mặt trên sân tại thời điểm phân giải** thì hiệu ứng mới có hiệu lực. Vì lá bài đã bị phá hủy và rời sân trước khi Chain Link giải quyết, toàn bộ hiệu ứng bên trong nó lập tức bị vô hiệu hóa, bất chấp logic độc lập của từ nối.

---

## Câu hỏi 5: Kiểm tra khả năng nhận diện Hiệu ứng Không Kích hoạt (Non-Activated Effects)

### Tình huống
Một lá bài quái thú sở hữu một dòng văn bản duy nhất như sau:
*"Monsters your opponent controls lose 500 ATK. You can only use this effect once per turn."*

### Câu hỏi
Khi người chơi đưa quái thú này ra sân ở trạng thái ngửa mặt, đối thủ có quyền kích hoạt một lá bài Quick Effect có tác dụng: *"Negate the activation of a monster effect"* (Phủ nhận sự kích hoạt hiệu ứng của quái thú) để ngăn chặn dòng văn bản giảm công trên không? Vì sao?

### Câu trả lời kỳ vọng (Expected Output)
- **Phán quyết:** **KHÔNG THỂ.** Đối thủ không thể kích hoạt lá bài phủ nhận trong tình huống này.
- **Giải thích:** Theo quy tắc văn bản hệ thống PSCT, một hiệu ứng được coi là có kích hoạt (tạo Chain Link) bắt buộc phải có dấu hai chấm (`:`) thể hiện điều kiện hoặc dấu chấm phẩy (`;`) thể hiện chi phí/mục tiêu. Dòng văn bản của quái thú này hoàn toàn **không có dấu `:` lẫn dấu `;`**, chứng tỏ đây là một **Hiệu ứng liên tục (Continuous Effect) / Hiệu ứng không kích hoạt (Non-Activated Effect)**. Hiệu ứng này sẽ tự động áp dụng lên sân ngay khi quái thú xuất hiện mà không mở ra bất kỳ Chain Link nào. Vì không có hành động "kích hoạt" (activation), đối thủ không thể sử dụng các quân bài chỉ có tác dụng phủ nhận sự kích hoạt để tương tác.

---

## Câu hỏi 6: Continuous Effect chặn Trigger Effect khi Summon

### Tình huống
Người chơi A có quái thú trên sân với Hiệu ứng liên tục: *"Quái thú của đối thủ không thể kích hoạt hiệu ứng trên sân."*

Người chơi B triệu hồi quái thú có Trigger Effect: *"When this card is Summoned: You can destroy 1 card on the field."*

Ngay khi quái thú B chạm sân hợp lệ, B tuyên bố kích hoạt hiệu ứng để phá 1 lá trên sân.

### Câu hỏi
Người chơi B có được phép kích hoạt và xếp hiệu ứng quái thú đó vào Chain Link không? Phân tích dựa trên timing của Continuous Effect vs Trigger Effect.

### Câu trả lời kỳ vọng (Expected Output)
- **Phán quyết:** **KHÔNG ĐƯỢC PHÉP (NO)** — B không thể kích hoạt Trigger Effect và không xếp được vào Chain.
- **Giải thích:** Continuous Effect áp dụng liên tục, không tạo Chain. Trigger "When Summoned: You can..." vẫn cần **kích hoạt** (activation) — đó là hiệu ứng kích hoạt trên sân. Luật cấm kích hoạt đã có hiệu lực ngay khi quái thú B chạm sân, trước khi B kịp declare activation. Không được mở đầu bằng "Có." rồi giải thích ngược.

---

## Kết quả đánh giá tự động (Lab API)

Chạy: `python3 Test/run_lab_eval.py --rag-limit 5`

| Câu | Chủ đề | Trạng thái |
|-----|--------|------------|
| 1 | SEGOC | PASS — thứ tự B→D→C→A, không hoán đổi giữa category |
| 2 | PSCT Cost/Target | PASS — cost không hoàn, target không đổi khi negate |
| 3 | And if you do vs Then | PASS |
| 4 | Continuous + And also | PASS |
| 5 | Non-Activated Effect | PASS |
| 6 | Continuous chặn Trigger Summon | PASS — mở đầu **KHÔNG ĐƯỢC PHÉP (NO)**, không mâu thuẫn "Có." |

**Format phán quyết bắt buộc:** câu hỏi yes/no phải mở đầu bằng `**ĐƯỢC PHÉP (YES)**:` hoặc `**KHÔNG ĐƯỢC PHÉP (NO)**:` — không dùng "Có./Không." đơn lẻ.

**Nguồn RAG bắt buộc:** ingest `Test/data/ygo_core_rulebook_summary.md` + `SD_RuleBook_EN_10.md` (filename `sd_rulebook_EN_10.md`) + `Conjunctions.md`.

**Rubric:** khớp ngữ nghĩa (keyword/concept), không yêu cầu đúng từng chữ.
