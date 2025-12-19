"""
GraphIO Ontology SDK 사용 예제 (실제 데이터 조회)
"""

import json
from graphio_sdk import GraphioClient, LogicalCondition

client = GraphioClient()


def example_basic_data_query():
    """예제 1: 기본 데이터 조회"""
    print("\n" + "=" * 80)
    print("예제 1: 기본 데이터 조회")
    print("=" * 80)

    try:
        # 한글 ObjectType 이름도 지원
        alarm_zone = client.ontology.get_object_type("유닛")

        if not alarm_zone:
            print("✗ '유닛' ObjectType을 찾을 수 없습니다.")
            return

        print(f"✓ '유닛' ObjectType 로드 완료")
        print(f"  - ObjectType ID: {alarm_zone._object_type_id}")
        print(f"  - Properties: {alarm_zone._properties}")

        # 실제 데이터 조회 - select('*')로 모든 필드 선택
        print("\n[실제 데이터 조회 - 모든 필드]")
        results = (alarm_zone
                   .where(alarm_zone.x > 650)
                   .select('*')
                   .limit(10)
                   .execute())

        print(f"✓ 조회 완료: {len(results)}건")
        print(f"\n결과:")
        for i, result in enumerate(results, 1):
            print(f"  {i}. {result}")

        if results:
            print(f"\n첫 번째 레코드 전체:")
            print(json.dumps(results[0], indent=2, ensure_ascii=False))

    except Exception as e:
        print(f"✗ 에러: {e}")
        import traceback
        traceback.print_exc()


def example_select_all_fields():
    """예제 2: 모든 필드 선택 (select('*'))"""
    print("\n" + "=" * 80)
    print("예제 2: 모든 필드 선택")
    print("=" * 80)

    try:
        Employee = client.ontology.get_object_type("Employee")

        if not Employee:
            print("✗ Employee ObjectType을 찾을 수 없습니다.")
            return

        # select('*')로 모든 필드 선택
        print("[1] 모든 필드 선택")
        all_fields = (Employee
                      .where(Employee.age > 30)
                      .select('*')
                      .limit(5)
                      .execute())

        print(f"✓ {len(all_fields)}건 조회")
        if all_fields:
            print(f"  필드 목록: {list(all_fields[0].keys())}")
            print(f"\n  첫 번째 레코드:")
            print(json.dumps(all_fields[0], indent=2, ensure_ascii=False))

        # 특정 필드만 선택
        print("\n[2] 특정 필드만 선택")
        specific_fields = (Employee
                           .where(Employee.age > 30)
                           .select("name", "age", "email")
                           .limit(5)
                           .execute())

        print(f"✓ {len(specific_fields)}건 조회")
        for emp in specific_fields:
            print(f"  - {emp.get('name')}: {emp.get('age')}세, {emp.get('email')}")

    except Exception as e:
        print(f"✗ 에러: {e}")
        import traceback
        traceback.print_exc()


def example_complex_queries():
    """예제 3: 복잡한 쿼리"""
    print("\n" + "=" * 80)
    print("예제 3: 복잡한 쿼리")
    print("=" * 80)

    try:
        Employee = client.ontology.get_object_type("Employee")

        if not Employee:
            print("✗ Employee ObjectType을 찾을 수 없습니다.")
            return

        # 1. AND 조건
        print("[1] AND 조건: age > 30 AND department = 'Engineering'")
        result = (Employee
                  .where(
            LogicalCondition("and", [
                Employee.age > 30,
                Employee.department == "Engineering"
            ])
        )
                  .select("name", "age", "department")
                  .limit(5)
                  .execute())

        print(f"✓ {len(result)}건 조회")
        for emp in result:
            print(f"  - {emp.get('name')}: {emp.get('age')}세, {emp.get('department')}")

        # 2. OR 조건
        print("\n[2] OR 조건: age < 25 OR age > 50")
        result = (Employee
                  .where(
            LogicalCondition("or", [
                Employee.age < 25,
                Employee.age > 50
            ])
        )
                  .select("name", "age")
                  .limit(5)
                  .execute())

        print(f"✓ {len(result)}건 조회")
        for emp in result:
            print(f"  - {emp.get('name')}: {emp.get('age')}세")

        # 3. 중첩 조건
        print("\n[3] 중첩 조건: (age > 40 OR department = 'Sales') AND active = true")
        result = (Employee
                  .where(
            LogicalCondition("and", [
                LogicalCondition("or", [
                    Employee.age > 40,
                    Employee.department == "Sales"
                ]),
                Employee.active == True
            ])
        )
                  .select("name", "age", "department", "active")
                  .limit(5)
                  .execute())

        print(f"✓ {len(result)}건 조회")
        for emp in result:
            print(f"  - {emp.get('name')}: {emp.get('age')}세, {emp.get('department')}, Active: {emp.get('active')}")

        # 4. LIKE 검색
        print("\n[4] LIKE 검색: name LIKE 'John%'")
        result = (Employee
                  .where(Employee.name.like("John%"))
                  .select("name", "email")
                  .limit(5)
                  .execute())

        print(f"✓ {len(result)}건 조회")
        for emp in result:
            print(f"  - {emp.get('name')}: {emp.get('email')}")

        # 5. IN 조건
        print("\n[5] IN 조건: department IN ['Sales', 'Marketing', 'HR']")
        result = (Employee
                  .where(Employee.department.is_in(["Sales", "Marketing", "HR"]))
                  .select("name", "department")
                  .limit(5)
                  .execute())

        print(f"✓ {len(result)}건 조회")
        for emp in result:
            print(f"  - {emp.get('name')}: {emp.get('department')}")

    except Exception as e:
        print(f"✗ 에러: {e}")
        import traceback
        traceback.print_exc()


def example_utility_methods():
    """예제 4: 유틸리티 메서드 (count, first, exists)"""
    print("\n" + "=" * 80)
    print("예제 4: 유틸리티 메서드")
    print("=" * 80)

    try:
        Employee = client.ontology.get_object_type("Employee")

        if not Employee:
            print("✗ Employee ObjectType을 찾을 수 없습니다.")
            return

        # 1. count() - 개수 세기
        print("[1] count(): 30세 이상 직원 수")
        count = (Employee
                 .where(Employee.age >= 30)
                 .select("name")  # 필드는 필요하지만 count만 반환
                 .count())
        print(f"✓ 30세 이상 직원: {count}명")

        # 2. first() - 첫 번째 레코드
        print("\n[2] first(): 첫 번째 직원")
        first_emp = (Employee
                     .where(Employee.age > 0)
                     .select("name", "age", "department")
                     .first())

        if first_emp:
            print(f"✓ {first_emp.get('name')}: {first_emp.get('age')}세, {first_emp.get('department')}")
        else:
            print("✗ 데이터 없음")

        # 3. exists() - 존재 여부 확인
        print("\n[3] exists(): Engineering 부서 직원 존재 여부")
        has_engineers = (Employee
                         .where(Employee.department == "Engineering")
                         .select("name")
                         .exists())
        print(f"✓ Engineering 부서 직원 {'존재함' if has_engineers else '없음'}")

        # 4. limit과 함께 사용
        print("\n[4] limit(): 상위 3명만 조회")
        top_3 = (Employee
                 .select("name", "age", "email")
                 .limit(3)
                 .execute())

        print(f"✓ {len(top_3)}건 조회")
        for i, emp in enumerate(top_3, 1):
            print(f"  {i}. {emp.get('name')}")

    except Exception as e:
        print(f"✗ 에러: {e}")
        import traceback
        traceback.print_exc()


def example_pagination():
    """예제 5: 페이지네이션 구현"""
    print("\n" + "=" * 80)
    print("예제 5: 페이지네이션")
    print("=" * 80)

    try:
        Employee = client.ontology.get_object_type("Employee")

        if not Employee:
            print("✗ Employee ObjectType을 찾을 수 없습니다.")
            return

        page_size = 5
        page = 1

        print(f"페이지 크기: {page_size}개")
        print(f"\n[페이지 {page}]")

        # 첫 페이지
        employees = (Employee
                     .select("name", "age", "department")
                     .limit(page_size)
                     .execute())

        print(f"✓ {len(employees)}건 조회")
        for i, emp in enumerate(employees, 1):
            print(f"  {i}. {emp.get('name')} - {emp.get('age')}세 - {emp.get('department')}")

        # Note: 실제 페이지네이션을 위해서는 offset이 필요하지만
        # 현재 API가 offset을 지원하지 않으므로 limit만 사용
        print("\n* 참고: offset 파라미터가 추가되면 완전한 페이지네이션 구현 가능")

    except Exception as e:
        print(f"✗ 에러: {e}")
        import traceback
        traceback.print_exc()


def example_multiple_object_types():
    """예제 6: 여러 ObjectType 동시 사용"""
    print("\n" + "=" * 80)
    print("예제 6: 여러 ObjectType 동시 사용")
    print("=" * 80)

    try:
        # 여러 ObjectType 로드
        Employee = client.ontology.get_object_type("Employee")
        Ticket = client.ontology.get_object_type("Ticket")

        if Employee:
            print("[Employee 데이터]")
            employees = (Employee
                         .select("name", "department")
                         .limit(3)
                         .execute())
            print(f"✓ {len(employees)}건 조회")
            for emp in employees:
                print(f"  - {emp.get('name')} ({emp.get('department')})")

        if Ticket:
            print("\n[Ticket 데이터]")
            tickets = (Ticket
                       .where(Ticket.status == "open")
                       .select("ticket_id", "title", "priority")
                       .limit(3)
                       .execute())
            print(f"✓ {len(tickets)}건 조회")
            for ticket in tickets:
                print(f"  - #{ticket.get('ticket_id')}: {ticket.get('title')} [{ticket.get('priority')}]")

        print(f"\n캐시된 ObjectType: {client.ontology.list_object_types()}")

    except Exception as e:
        print(f"✗ 에러: {e}")
        import traceback
        traceback.print_exc()


def example_error_handling():
    """예제 7: 에러 처리"""
    print("\n" + "=" * 80)
    print("예제 7: 에러 처리")
    print("=" * 80)

    try:
        # 1. 존재하지 않는 ObjectType
        print("[1] 존재하지 않는 ObjectType")
        NonExistent = client.ontology.get_object_type("NonExistentType")

        if NonExistent:
            print("✓ ObjectType 로드 성공")
        else:
            print("✗ ObjectType을 찾을 수 없습니다 (정상 동작)")

        # 2. select 없이 실행
        print("\n[2] select 없이 execute() 호출")
        try:
            Employee = client.ontology.get_object_type("Employee")

            if Employee:
                result = Employee.where(Employee.age > 30).execute()
        except ValueError as e:
            print(f"✗ 예상된 에러: {e}")

        # 3. 잘못된 필드 조회는 서버에서 처리
        print("\n[3] 존재하지 않는 필드 조회")
        try:
            Employee = client.ontology.get_object_type("Employee")

            if Employee:
                result = (Employee
                          .select("name", "nonexistent_field")
                          .limit(1)
                          .execute())
                print(f"✓ 조회 완료: {len(result)}건 (서버가 처리)")
        except Exception as e:
            print(f"✗ 서버 에러: {e}")

    except Exception as e:
        print(f"✗ 에러: {e}")
        import traceback
        traceback.print_exc()


def example_korean_object_types():
    """예제 8: 한글 ObjectType 이름 사용"""
    print("\n" + "=" * 80)
    print("예제 8: 한글 ObjectType 이름 사용")
    print("=" * 80)

    try:
        # 한글 ObjectType 이름으로 로드
        unit = client.ontology.get_object_type("유닛")

        if not unit:
            print("✗ '유닛' ObjectType을 찾을 수 없습니다.")
            return

        print(f"✓ '유닛' ObjectType 로드 완료")
        print(f"  - ObjectType ID: {unit._object_type_id}")
        print(f"  - Properties: {unit._properties}")

        # 모든 필드 선택
        print("\n[모든 필드 조회]")
        results = (unit
                   .where(unit.x > 650)
                   .select('*')
                   .limit(5)
                   .execute())

        print(f"✓ {len(results)}건 조회")
        for i, result in enumerate(results, 1):
            print(f"  {i}. x={result.get('x')}, y={result.get('y')}")

        # 특정 필드만 선택
        print("\n[특정 필드만 조회]")
        if 'x' in unit._properties and 'y' in unit._properties:
            results = (unit
                       .where(unit.x > 650)
                       .select("x", "y")
                       .limit(5)
                       .execute())

            print(f"✓ {len(results)}건 조회")
            for i, result in enumerate(results, 1):
                print(f"  {i}. x={result.get('x')}, y={result.get('y')}")

    except Exception as e:
        print(f"✗ 에러: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("GraphIO Ontology SDK - 실제 데이터 조회 예제")
    print("=" * 80)

    # 기본 예제 실행
    example_basic_data_query()

    # 다른 예제들 (주석 해제하여 실행)
    # example_select_all_fields()
    # example_complex_queries()
    # example_utility_methods()
    # example_pagination()
    # example_multiple_object_types()
    # example_error_handling()
    # example_korean_object_types()

    print("\n" + "=" * 80)
    print("모든 예제 완료!")
    print("=" * 80)
