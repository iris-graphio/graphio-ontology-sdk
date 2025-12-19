"""
'유닛' 데이터의 x, y 좌표를 조회하여 수정하고 업데이트하는 함수
"""

from graphio_sdk import GraphioClient


def update_unit_xy():
    from random import choice, randint
    """
    '유닛' 데이터를 조회하여 x, y 좌표를 수정하고 업데이트합니다.

    Args:
        x_modifier: x 값을 수정하는 함수. 예: lambda x: x + 10
                    None이면 x 값을 변경하지 않습니다.
        y_modifier: y 값을 수정하는 함수. 예: lambda y: y * 2
                    None이면 y 값을 변경하지 않습니다.
        condition: 조회 조건 (Condition 객체). 예: Unit.x > 650
                   None이면 모든 유닛을 조회합니다.
        limit: 조회할 최대 개수. None이면 제한 없음.

    Returns:
        dict: 업데이트 결과
            - updated_count: 업데이트된 레코드 수
            - results: 업데이트 결과 상세 정보

    Example:
        from graphio_sdk import GraphioClient

        client = GraphioClient()
        Unit = client.ontology.get_object_type("유닛")

        # x 값을 10씩 증가시키기
        result = update_unit_xy(x_modifier=lambda x: x + 10)

        # 특정 조건의 유닛만 수정
        result = update_unit_xy(
            x_modifier=lambda x: x + 5,
            y_modifier=lambda y: y - 3,
            condition=Unit.x > 650,
            limit=10
        )
    """
    client = GraphioClient()

    try:
        # '유닛' ObjectType 가져오기
        Unit = client.ontology.get_object_type("유닛")

        if not Unit:
            raise ValueError("'유닛' ObjectType을 찾을 수 없습니다.")

        # 조회 쿼리 구성
        query = Unit.select('y', 'x')

        # 데이터 조회
        units = query.execute()

        if not units:
            print("수정할 '유닛' 데이터가 없습니다.")
            return {
                "updated_count": 0,
                "results": None
            }

        print(f"조회된 '유닛' 데이터: {len(units)}건")

        # 편집 세션 시작
        edits = client.ontology.edits()

        updated_count = 0
        bounds = (0, 1000)

        # 각 유닛의 x, y 값 수정
        for unit_data in units:
            if not unit_data['elementId']:
                print(f"경고: elementId가 없는 레코드를 건너뜁니다: {unit_data}")
                continue

            if unit_data.get('side') == 'ALLY':
                continue

            dx = choice([-1, 1]) * randint(10, 100)  # -100 ~ -10 또는 10 ~ 100
            dy = choice([-1, 1]) * randint(10, 100)
            # 현재 x, y 값 가져오기
            unit_data['x'] = max(bounds[0], min(bounds[1], unit_data.properties.x + dx))
            unit_data['y'] = max(bounds[0], min(bounds[1], unit_data.properties.y + dy))

            if updated:
                # 편집 빌더에 업데이트 추가
                edits.objects.유닛.edit({
                    "elementId": element_id,
                    "properties": properties
                })
                updated_count += 1

        if updated_count == 0:
            print("수정할 데이터가 없습니다.")
            return {
                "updated_count": 0,
                "results": None
            }

        # 변경사항 커밋
        print(f"\n{updated_count}건의 변경사항을 커밋합니다...")
        results = edits.commit()

        print(f"✓ 업데이트 완료: {updated_count}건")

        return {
            "updated_count": updated_count,
            "results": results
        }

    except Exception as e:
        print(f"✗ 에러 발생: {e}")
        import traceback
        traceback.print_exc()
        raise

    finally:
        client.close()


if __name__ == "__main__":
    """
    사용 예제
    """
    print("\n" + "=" * 80)
    print("예제 코드는 주석 처리되어 있습니다. 필요에 따라 주석을 해제하여 실행하세요.")
    print("=" * 80)
    update_unit_xy()
