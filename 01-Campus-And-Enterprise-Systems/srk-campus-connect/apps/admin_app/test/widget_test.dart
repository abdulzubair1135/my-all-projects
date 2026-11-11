import 'package:flutter_test/flutter_test.dart';
import 'package:admin_app/main.dart';

void main() {
  testWidgets('AdminApp smoke test', (WidgetTester tester) async {
    await tester.pumpWidget(const AdminApp());
    expect(find.text('SRK Principal Portal'), findsNothing);
  });
}
